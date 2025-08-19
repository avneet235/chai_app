from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ChaiVariety, Store
from .forms import ChaiVarietyForm
import os, json, requests
from django.http import HttpResponse


def all_chai(request):
    chais = ChaiVariety.objects.all()
    return render(request, 'chai/all_chai.html',{'chais': chais})

def chai_detail(request, chai_id):
  chai = get_object_or_404(ChaiVariety, pk=chai_id)
  return render(request, 'chai/chai_detail.html', {'chai': chai})

def chai_store_view(request):
  stores = None
  if request.method == 'POST':
    form = ChaiVarietyForm(request.POST)
    if form.is_valid():
      chai_variety = form.cleaned_data['chai_variety']
      stores = Store.objects.filter(chai_varieties=chai_variety)
  else:
    form = ChaiVarietyForm()

    return render(request, 'chai/chai_stores.html', {'form': form, 'stores': stores})


@csrf_exempt
@require_POST
def upload_to_gdrive(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        access_token = data.get("access_token")
        folder_id = data.get("folder_id")
        zip_file_path = data.get("zip_file_path")

        if not all([access_token, folder_id, zip_file_path]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if not os.path.exists(zip_file_path):
            return JsonResponse({"error": "File not found"}, status=404)

        headers = {"Authorization": f"Bearer {access_token}"}
        metadata = {
            "name": os.path.basename(zip_file_path),
            "parents": [folder_id]
        }

        files = {
            "data": ("metadata", json.dumps(metadata), "application/json"),
            "file": open(zip_file_path, "rb")
        }

        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        response = requests.post(upload_url, headers=headers, files=files)

        if response.status_code == 200:
            file_data = response.json()
            return JsonResponse({
                "file_id": file_data["id"],
                "file_name": file_data["name"]
            })
        else:
            return JsonResponse({"error": response.text}, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def oauth2callback(request):
    auth_code = request.GET.get("code")
    if not auth_code:
        return HttpResponse("No code found in request", status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": auth_code,
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://127.0.0.1:8000/oauth2callback/",
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "access_token" in token_info:
        return JsonResponse(token_info)
    else:
        return JsonResponse({"error": token_info}, status=400)
