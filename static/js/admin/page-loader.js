function init() {
    addHandlers();
    
    var lists = window.listElements;
    
    for (var list in lists) {
        listLoader.makeTable(list);
    }
    
    pageLoader.renderElements(window.staticElements);
}

var pageLoader = {
    
    renderElements: function(elements) {
        for (var element in elements) {
            var section = document.getElementById(element);
            for (var item in elements[element]["data"]) {
                var dict = elements[element]["data"][item];
            
                var div = document.createElement("div");
                div.className = "item";
                
                var header = document.createElement("div");
                header.className = "item-header";
                header.appendChild(document.createTextNode(dict["display"]));
                var content = document.createElement("div");
                content.className = "item-content";
                fillContent(element, content, dict["data"]);
                
                div.appendChild(header);
                div.appendChild(content);
                
                section.appendChild(div);
            }
        }
    },

    updateLocal: function() {
        var staticElements = window.staticElements;
        var lists = window.listElements;
        
        for (var element in staticElements) {
            var sections = document.getElementById(element).getElementsByClassName("item-content");
            console.log(sections);
            var k = 0;
            for (var item in staticElements[element]["data"]) {
                staticElements[element]["data"][item]["data"] = getDataFormatted(element, sections[k]);
                k++;
            }
        }
        
        var listSection = document.getElementById("lists").getElementsByClassName("list-selection");
        
        var i = 0;
        for (var list in lists) {
            var divs = listSection[i].getElementsByTagName("div");
            
            var x = 0;
            for (var variable in lists[list]) {
                if (variable.charAt(0) != "_") {
                    lists[list][variable]["data"] = [];
                    for (var j = 0; j < divs.length; j++) {
                        var inputs = divs[j].getElementsByTagName("textarea");
                        lists[list][variable]["data"].push(inputs[x].value);
                    }
                    
                    x++;
                }
            }
            
            i++;
        }
        
    },
    
    save: function(page) {
        if (confirm("Are you sure that you want to save? There is no way to revert after these changes are made.")) {
            pageLoader.uploadImages();
        }
    },
        
    uploadImages: function() {
        var forms = document.getElementsByClassName("image-upload");
        document.getElementById("message-box").innerHTML = "Uploading (1/" + forms.length + ")...";
            
        for (var count = 0; count < forms.length; count++) {
            $.ajax({
                url: $SCRIPT_ROOT + "/admin/upload-image",
                type: 'POST',
        
                data: new FormData(forms[count]),
        
                cache: false,
                contentType: false,
                processData: false,
                index: count,
                
                xhr: function() {
                    var i = this.index;
                    var xhr = $.ajaxSettings.xhr();
                    if (xhr.upload) {
                        xhr.upload.addEventListener('progress', function(event) {
                            var percent = 0;
                            var position = event.loaded || event.position; /*event.position is deprecated*/
                            var total = event.total;
                            if (event.lengthComputable) {
                                percent = Math.ceil(position / total * 100);
                                forms[i].getElementsByClassName("progress")[0].innerHTML = percent + "%";
                            }                    
                        }, false);
                    }
                    return xhr;
                },
                
                success: function(data) {
                    var i = this.index;
                    
                    forms[i].getElementsByClassName("progress")[0].innerHTML = "";
                    forms[i].getElementsByTagName("input")[0].value = "";
                    
                    if (data.filename != "") {
                        forms[i].getElementsByClassName("image-placeholder")[0].value = data.filename;
                    }
                    
                    if (i + 1 == forms.length) {
                        document.getElementById("message-box").innerHTML = "Saving...";
                        pageLoader.updateLocal();
                        pageLoader.saveData();
                    } else {
                        document.getElementById("message-box").innerHTML = "Uploading Images (" + (i+1).toString() + "/" + forms.length.toString() + ")..."
                    }
                }
            });
        
        }
    },
    
    saveData: function() {
        var tmpList = {};
            for (var item in window.listElements) {
                tmpList[item] = {};
                for (var variable in window.listElements[item]) {
                    if (variable.charAt(0) != "_") {
                        tmpList[item][variable] = window.listElements[item][variable];
                    }
                }
            }
            
            document.getElementById("message-box").innerHTML = "Saving...";
            
            $.ajax({ url: $SCRIPT_ROOT + "/admin/save-data",
                data: {
                    list_elements: JSON.stringify(tmpList),
                    static_elements: JSON.stringify(window.staticElements),
                    page_name: window.page
                },
                success: function(data){
                    document.getElementById("message-box").innerHTML = "Saved.";
                }, dataType: "json", type: "post"});
    }
    
};