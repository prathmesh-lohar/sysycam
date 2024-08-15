import io
import time
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from django.shortcuts import render
from threading import Lock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Buffer to store the latest frame and a lock for thread-safe operations
frame_buffer = None
frame_lock = Lock()

def camera_page(request):
    return render(request, 'index.html')

@csrf_exempt
def upload_frame(request):
    global frame_buffer
    start_time = time.time()
    
    if request.method == 'POST':
        if 'frame' in request.FILES:
            image = request.FILES['frame']
            
            # Directly read the uploaded frame without unnecessary conversions
            file_bytes = np.frombuffer(image.read(), np.uint8)
            img_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Encode the frame as JPEG (quality can be adjusted)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]  # Adjust quality if needed
            _, jpeg = cv2.imencode('.jpg', img_cv, encode_param)

            # Store the latest frame in the buffer
            with frame_lock:
                frame_buffer = jpeg.tobytes()
            
            processing_time = time.time() - start_time
            logging.info(f"Frame processed in {processing_time:.2f} seconds")
            
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
            # Adjust sleep time if needed
            time.sleep(0.005)  # Reduced sleep time to improve frame rate
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
