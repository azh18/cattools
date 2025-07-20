import os
import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

BASE_DIR = Path(__file__).resolve().parent.parent
RUNS_DIR = BASE_DIR / 'runs'

# Ensure directories exist
RUNS_DIR.mkdir(exist_ok=True)


import requests

def index(request):
    try:
        response = requests.get('https://v1.hitokoto.cn/')
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        quote = f"{data['hitokoto']} - {data['from']}"
    except requests.exceptions.RequestException as e:
        quote = "生活，一半是回忆，一半是继续。"
    return render(request, 'index.html', {'quote': quote})

# 用于处理基金持有人大会数据
def excel_tool_page(request):
    return render(request, 'excel_tool.html')


def upload_files(request):
    if request.method == 'POST':
        src_file = request.FILES.get('src_file')
        target_file = request.FILES.get('target_file')

        if not src_file or not target_file:
            return JsonResponse({'error': 'Both files are required.'}, status=400)

        task_id = str(uuid.uuid4())
        run_dir = RUNS_DIR / task_id
        run_dir.mkdir()

        src_path = run_dir / 'src.xlsx'
        target_path = run_dir / 'target.xlsx'

        with open(src_path, 'wb+') as destination:
            for chunk in src_file.chunks():
                destination.write(chunk)

        with open(target_path, 'wb+') as destination:
            for chunk in target_file.chunks():
                destination.write(chunk)

        log_path = run_dir / 'run.log'
        result_path = run_dir / 'result.xlsx'
        script_path = BASE_DIR.parent / 'catwork2.py'

        # Modify the command to match the original script's expectation
        command = [
            'python',
            '-u',
            str(script_path),
            str(src_path),
            str(target_path),
            str(result_path)
        ]

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        with open(log_path, 'w', encoding='utf-8') as log_file:
            subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT, cwd=run_dir, env=env)

        return JsonResponse({'task_id': task_id})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'status': 'FAILURE', 'log': 'Task ID is missing.'})

    run_dir = RUNS_DIR / task_id
    log_path = run_dir / 'run.log'
    result_path = run_dir / 'result.xlsx'

    log_content = ''
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()

    print(log_content)
    if result_path.exists():
        return JsonResponse({'status': 'SUCCESS', 'log': log_content})
    
    if 'Traceback' in log_content or 'Error' in log_content:
        return JsonResponse({'status': 'FAILURE', 'log': log_content})

    return JsonResponse({'status': 'PROCESSING', 'log': log_content})


def download_result(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return HttpResponse('Task ID is missing.', status=400)

    run_dir = RUNS_DIR / task_id
    result_path = run_dir / 'result.xlsx'

    if result_path.exists():
        with open(result_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="result.xlsx"'
            return response
    else:
        return HttpResponse('Result file not found.', status=404)
