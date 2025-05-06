function add_product(user_id) {
  const add_product_window = window.open(
    `/seller/product/add/${user_id}/`,
    "New product",
    "width=600,height=500,left=0,top=0"
  );
  let interval = setInterval(function () {
    if (add_product_window.closed) {
      clearInterval(interval); // Dừng kiểm tra khi cửa sổ bị đóng
      location.reload();
    }
  }, 1000); // Kiểm tra mỗi giây
}
function del(product_image_id) {
  if (confirm("Are you sure you want to delete this image?")) {
    fetch(`/delete_product_image/${product_image_id}/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    })
      .then((response) => {
        if (response.ok) {
          alert("Image deleted successfully!");
          location.reload(); // Reload the page to see the changes
        } else {
          alert("Failed to delete the image.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while deleting the image.");
      });
  }
}
function hide_product(product_id) {
  const hideButton = document.getElementById(`hide-button-${product_id}`);
  const statusElement = document.querySelector(
    `span.status[data-product-id="${product_id}"]`
  );
  const errorElement = document.getElementById(`error-${product_id}`);

  errorElement.style.display = "none";
  errorElement.textContent = "";

  fetch(`/hide_product/${product_id}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(), // Lấy CSRF token từ cookie
    },
  })
    .then((response) => {
      if (response.status === 400) {
        throw new Error("Error hiding product");
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        statusElement.textContent = data.new_status;
        hideButton.textContent = data.button_text;
      } else {
        errorElement.textContent = data.error || "Error hiding product";
        errorElement.style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      errorElement.textContent = error.message;
      errorElement.style.display = "block";
    });
}
function update_quantity(productId, change) {
  const quantityElement = document.querySelector(
    `span.quantity[data-product-id="${productId}"]`
  );
  const statusElement = document.querySelector(
    `span.status[data-product-id="${productId}"]`
  );
  const errorElement = document.getElementById(`error-${productId}`);

  errorElement.style.display = "none";
  errorElement.textContent = "";

  fetch(`/update_quantity/${productId}/${change}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(), // Lấy CSRF token từ cookie
    },
  })
    .then((response) => {
      if (response.status === 400) {
        throw new Error("Quantity cannot be negative");
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        quantityElement.textContent = data.new_quantity;
        statusElement.textContent = data.new_status;
      } else {
        errorElement.textContent = data.error || "Error updating quantity";
        errorElement.style.display = "block";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      errorElement.textContent = error.message;
      errorElement.style.display = "block";
    });
}