function addHandlers() {

    addHandler({
        type: "text",
        
        loadData: function(parent, data) {
            var textarea = document.createElement("textarea");
            textarea.className = "user-value"
            parent.appendChild(textarea);
            textarea.value = data;
        },
        
        formatData: function(content) {
            return content.getElementsByClassName("user-value")[0].value;
        }
    });
    
    addHandler({
        type: "image",
        
        loadData: function(parent, data) {
            var form = document.createElement("form");
            form.className = "image-upload";
            form.setAttribute("enc-type", "multipart/form-data");
            var selector = document.createElement("input");
            selector.setAttribute("type", "file");
            selector.setAttribute("name", "file");
            var span = document.createElement("span");
            span.className = "progress";
            var placeholder = document.createElement("textarea");
            placeholder.value = data;
            placeholder.classList.add("user-value", "image-placeholder");
            form.appendChild(selector);
            form.appendChild(span);
            form.appendChild(placeholder);
            parent.appendChild(form);
        },
        
        formatData: function(content) {
            return content.getElementsByClassName("user-value")[0].value;
        }
    });
}

function addHandler(data) {
    if (!window.handlers)
        window.handlers = {}
    window.handlers[data.type] = data;
}

function fillContent(type, content, data) {
    window.handlers[type].loadData(content, data);
}

function getDataFormatted(type, content) {
    console.log(window.handlers[type].formatData(content));
    return window.handlers[type].formatData(content);
}

