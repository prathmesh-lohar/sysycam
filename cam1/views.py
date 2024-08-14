import io
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import cv2
import numpy as np
from django.shortcuts import render
from threading import Lock

# Buffer to store the latest frame and a lock for thread-safe operations
frame_buffer = None
frame_lock = Lock()

def camera_page(request):
    return render(request, 'index.html')

@csrf_exempt
def upload_frame(request):
    global frame_buffer
    if request.method == 'POST':
        if 'frame' in request.FILES:
            image = request.FILES['frame']
            img = Image.open(image)

            img_cv = np.array(img)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

            # Encode the frame as JPEG
            _, jpeg = cv2.imencode('.jpg', img_cv)

            # Store the latest frame in the buffer
            with frame_lock:
                frame_buffer = jpeg.tobytes()

            return HttpResponse("Frame received.", status=200)

        return HttpResponse("No frame found in request.", status=400)
    
    return HttpResponse("This endpoint accepts POST requests to upload frames.", status=405)

def mjpeg_feed(request):
    def generate():
        while True:
            with frame_lock:
                if frame_buffer:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
