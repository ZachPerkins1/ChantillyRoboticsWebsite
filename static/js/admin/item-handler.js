function addHandlers() {

    addHandler("text", function(parent) {
        var textarea = document.createElement("textarea");
        textarea.className = "user-input"
        parent.appendChild(textarea);
    });
    
    addHandler("image", function(parent) {
        var form = document.createElement("form");
        form.className = "image-upload";
        form.setAttribute("enc-type", "multipart/form-data");
        var selector = document.createElement("input");
        selector.setAttribute("type", "file");
        selector.setAttribute("name", "file");
        var span = document.createElement("span");
        span.className = "progress";
        var placeholder = document.createElement("textarea");
        placeholder.classList.add("user-input", "image-placeholder");
        form.appendChild(selector);
        form.appendChild(span);
        form.appendChild(placeholder);
        parent.appendChild(form);
    });

}

function addHandler(name, func) {
    if (!window.handlers)
        window.handlers = {}
    window.handlers[name] = func;
}

function fillContent(type, content) {
    var r;
    r = window.handlers[type].call(r, content);
}


