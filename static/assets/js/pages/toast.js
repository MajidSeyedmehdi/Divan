const toastTrigger = document.getElementById("btn-single-toast");
const toastContainer = document.getElementById("single-toast");

if (toastTrigger) {
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastContainer);
    toastTrigger.addEventListener("click", () => {
        toastBootstrap.show()
    });
}



const btnToastStack = document.getElementById("btn-stack-toast");
const toastStackContainer = document.getElementById("toast-stack-container");
const targetElement = document.querySelector('[data-docs-toast="stack"]');

// Remove base element markup
targetElement.parentNode.removeChild(targetElement);

// Handle btnToastStack click
btnToastStack.addEventListener("click", e => {
    e.preventDefault();

    const newToast = targetElement.cloneNode(true);
    toastStackContainer.append(newToast);
    const toast = bootstrap.Toast.getOrCreateInstance(newToast);
    toast.show();
});
