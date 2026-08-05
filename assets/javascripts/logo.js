document.addEventListener("DOMContentLoaded", function() {
    var title = document.querySelector(".md-header__topic:first-child");

    if (title) {
        title.addEventListener("click", function() {
            window.location.href = "/";
        });
    }
});