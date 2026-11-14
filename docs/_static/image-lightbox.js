document.addEventListener("DOMContentLoaded", function () {
    const imageLinks = document.querySelectorAll("figure a.image-reference");

    if (!imageLinks.length || !("HTMLDialogElement" in window)) {
        return;
    }

    const dialog = document.createElement("dialog");
    const image = document.createElement("img");
    const closeButton = document.createElement("button");

    dialog.className = "image-lightbox";
    dialog.setAttribute("aria-label", "Image preview");
    image.alt = "";
    closeButton.className = "image-lightbox__close";
    closeButton.type = "button";
    closeButton.textContent = "Close";
    closeButton.setAttribute("aria-label", "Close image preview");
    dialog.append(closeButton, image);
    document.body.append(dialog);

    let activeLink = null;

    imageLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            if (
                event.button !== 0 ||
                event.altKey ||
                event.ctrlKey ||
                event.metaKey ||
                event.shiftKey
            ) {
                return;
            }

            event.preventDefault();
            activeLink = link;
            image.src = link.href;

            const thumbnail = link.querySelector("img");
            image.alt = thumbnail ? thumbnail.alt : "";
            dialog.showModal();
            closeButton.focus();
        });
    });

    closeButton.addEventListener("click", function () {
        dialog.close();
    });

    document.addEventListener(
        "keydown",
        function (event) {
            if (event.key === "Escape" && dialog.open) {
                event.preventDefault();
                dialog.close();
            }
        },
        true
    );

    dialog.addEventListener("cancel", function (event) {
        event.preventDefault();
        dialog.close();
    });

    dialog.addEventListener("click", function (event) {
        if (event.target === dialog) {
            dialog.close();
        }
    });

    dialog.addEventListener("close", function () {
        image.removeAttribute("src");

        if (activeLink && activeLink.isConnected) {
            activeLink.focus();
        }
    });
});
