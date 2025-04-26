let stream = null; // Lưu luồng webcam
let captureInterval = null; // Lưu interval chụp ảnh
let faceMatcher;
const userId = document.getElementById('user-id').dataset.myValue;
console.log(userId);
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
          text: "Đang xác thực!",
          className: "success",
          style: { background: "green" },
          duration: 3000,
        }).showToast();
        setTimeout(CaptureAndRecognize, 2000);
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

async function CaptureAndRecognize() {
  const video = document.getElementById("video");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Chuyển canvas thành đối tượng Image
  const image = new Image();
  image.src = canvas.toDataURL("image/png");
  // Đợi image tải xong
  await new Promise((resolve) => {
    image.onload = resolve;
  });

  const displayCanvas = faceapi.createCanvasFromMedia(image);

  const size = {
    width: image.width,
    height: image.height,
  };
  faceapi.matchDimensions(displayCanvas, size);

  const detections = await faceapi
    .detectAllFaces(image)
    .withFaceLandmarks()
    .withFaceDescriptors();
  const resizedDetections = faceapi.resizeResults(detections, size);

  for (const detection of resizedDetections) {
    const match = faceMatcher.findBestMatch(detection.descriptor);
    const matchLabel = match.toString();
    const expectedLabel = `user_${userId}`;
    const isMatch = matchLabel.includes(expectedLabel);

    const drawBox = new faceapi.draw.DrawBox(detection.detection.box, {
      label: matchLabel,
    });
    drawBox.draw(displayCanvas);

    Toastify({
      text: isMatch
        ? `Xác thực thành công!`
        : `Xác thực thất bại: Không phải User ${userId}`,
      className: isMatch ? "success" : "error",
      style: { background: isMatch ? "green" : "red" },
      duration: 5000,
    }).showToast();
      if (isMatch) {
        const response = await fetch(`/face/identification/${userId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // Thêm CSRF token nếu cần (dựa trên yêu cầu Django)
            "X-CSRFToken": getCSRFToken(), // Hàm lấy CSRF token, định nghĩa bên dưới
          },
        });
          location.href = `/customer/history/${userId}/`;
    }
  }
}

async function loadTrainingData() {
  try {
    // Gửi yêu cầu GET đến API Django để lấy danh sách ảnh của user
    const response = await fetch(`/user_faces/${userId}/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Thêm CSRF token nếu cần (dựa trên yêu cầu Django)
        "X-CSRFToken": getCSRFToken(), // Hàm lấy CSRF token, định nghĩa bên dưới
      },
    });

    if (!response.ok) {
      throw new Error("Không thể lấy dữ liệu ảnh từ server");
    }

    const data = await response.json();
    const faceDescriptors = [];

    // Giả sử API trả về danh sách các URL ảnh: [{url: "..."}, ...]
    for (const imageData of data) {
      const imageUrl = imageData.url; // URL của ảnh (e.g., "/media/face_images/...")
      const image = await faceapi.fetchImage(imageUrl);
      const detection = await faceapi
        .detectSingleFace(image)
        .withFaceLandmarks()
        .withFaceDescriptor();

      if (detection) {
        faceDescriptors.push(
          new faceapi.LabeledFaceDescriptors(`user_${userId}`, [
            detection.descriptor,
          ])
        );
        // Toastify({
        //   text: `Loaded face data for user ${userId}`,
        // }).showToast();
      }
    //   else {
    //     Toastify({
    //       text: `No face detected in image: ${imageUrl}`,
    //       className: "warning",
    //       style: { background: "orange" },
    //     }).showToast();
    //   }
    }

    return faceDescriptors;
  } catch (error) {
    Toastify({
      text: `Lỗi khi tải dữ liệu: ${error.message}`,
      className: "error",
      style: { background: "red" },
      duration: 5000,
    }).showToast();
    return [];
  }
}

// Khởi tạo mô hình
async function init() {
  await Promise.all([
    faceapi.loadSsdMobilenetv1Model("/face_id_model"),
    faceapi.loadFaceRecognitionModel("/face_id_model"),
    faceapi.loadFaceLandmarkModel("/face_id_model"),
  ]);
  const trainingData = await loadTrainingData();
  faceMatcher = new faceapi.FaceMatcher(trainingData, 0.6);

//   Toastify({
//     text: "Installed Detection Model!",
//   }).showToast();
}
init().then(() => {
  startWebcam();
});
