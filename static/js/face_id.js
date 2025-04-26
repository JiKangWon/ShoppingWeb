let stream = null; // Lưu luồng webcam
let captureInterval = null; // Lưu interval chụp ảnh
let captureCount = 0; // Đếm số ảnh đã chụp
let userId;
// Bật webcam
function startWebcam() {
  const video = document.getElementById("video");
  // Kiểm tra trình duyệt hỗ trợ getUserMedia
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((mediaStream) => {
        stream = mediaStream; // Lưu luồng
        video.srcObject = stream; // Gắn luồng vào video
        Toastify({
          text: "Webcam đã được bật!",
          className: "success",
          style: { background: "green" },
          duration: 3000,
        }).showToast();
      })
      .catch((error) => {
        Toastify({
          text: "Lỗi khi truy cập webcam: " + error.message,
          className: "error",
          style: { background: "red" },
          duration: 3000,
        }).showToast();
      });
  } else {
    Toastify({
      text: "Trình duyệt không hỗ trợ webcam!",
      className: "error",
      style: { background: "red" },
      duration: 3000,
    }).showToast();
  }
}
startWebcam(); 

// Hàm chụp ảnh và gửi lên server
function captureAndSend() {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const context = canvas.getContext("2d");
  if (!stream) {
    Toastify({
      text: "Lỗi: Webcam chưa được bật!",
      className: "error",
      style: { background: "red" },
      duration: 3000,
    }).showToast();
    return;
  }
  // Đặt kích thước canvas bằng video
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  // Vẽ frame hiện tại từ video lên canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Lấy ảnh dưới dạng base64
  const imageData = canvas.toDataURL("image/png");
  // Gửi dữ liệu (ảnh) lên server Django
  fetch(`/face/append/${userId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      image: imageData, // Gửi ảnh base64
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      captureCount++;
      // Kiểm tra nếu đã chụp đủ 15 ảnh
      if (captureCount >= 15) {
        clearInterval(captureInterval);
        Toastify({
          text: "Finished Verify",
          className: "success",
          style: { background: "green" },
          duration: 5000,
        }).showToast();
        captureCount = 0; // Reset đếm
      }
    })
    .catch((error) => {
      Toastify({
        text: "Lỗi khi gửi dữ liệu: " + error.message,
        className: "error",
        style: { background: "red" },
        duration: 3000,
      }).showToast();
      clearInterval(captureInterval); 
    });
}

// Bắt đầu chụp tự động
function startAutoCapture(user_id) {
  userId = user_id;
  if (!stream) {
    Toastify({
      text: "Lỗi: Webcam chưa được bật!",
      className: "error",
      style: { background: "red" },
      duration: 3000,
    }).showToast();
    return;
  }
  if (captureInterval) {
    Toastify({
      text: "Verification is happening! Wait a moment!!",
      className: "warning",
      style: { background: "orange" },
      duration: 3000,
    }).showToast();
    return;
  }
  captureCount = 0; // Reset đếm
  Toastify({
    text: "Start verify...",
    className: "info",
    style: { background: "blue" },
    duration: 3000,
  }).showToast();
  captureInterval = setInterval(captureAndSend, 1000); // Chụp mỗi giây
}
