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
                fillContent(element, content, dict);
                
                div.appendChild(header);
                div.appendChild(content);
                
                section.appendChild(div);
            }
        }
    },

    updateLocal: function(onSuccess) {
        var staticElements = window.staticElements;
        var lists = window.listElements;
        
        for (var element in staticElements) {
            var elementDiv = document.getElementById(element);
            if (elementDiv != undefined) {
                var sections = elementDiv.getElementsByClassName("item-content");
                console.log(sections);
                var k = 0;
                for (var item in staticElements[element]["data"]) {
                    getDataFormatted(element, sections[k], staticElements[element]["data"][item]);
                    k++;
                }
            }
        }
        
        var listSection = document.getElementById("lists").getElementsByClassName("list-selection");
        
        var i = 0;
        for (var list in lists) {
            var divs = listSection[i].getElementsByTagName("div");
            
            var x = 0;
            for (var variable in lists[list]) {
                if (variable.charAt(0) != "_") {
                    var type = lists[list][variable]["type"];
                    lists[list][variable]["data"] = [];
                    for (var j = 0; j < divs.length; j++) {
                        var inputs = divs[j].getElementsByClassName("item-content");
                        var item = clone(window.typeInfo[type]["empty"]);
                        var v = clone(lists[list][variable]);
                        v["data"] = item;
                        console.log(v)
                        getDataFormatted(type, inputs[x], v);
                        lists[list][variable]["data"].push(v["data"]);
                    }
                    
                    x++;
                }
            }
            
            i++;
        }
        
        onSuccess()
        
    },
    
    save: function(page) {
        if (confirm("Are you sure that you want to save? There is no way to revert after these changes are made.")) {
            pageLoader.saveData();
        }
    },
        
    uploadImages: function(onSuccess) {
        var forms = document.getElementsByClassName("image-upload");
        
        if (forms.length > 0) 
            document.getElementById("message-box").innerHTML = "Uploading...";
        
            
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
                    
                    if (i == forms.length - 1) 
                        onSuccess()
                }
            });
        
        }
    },
    
    saveData: function() {
        document.getElementById("message-box").innerHTML = "Uploading...";
        pageLoader.uploadImages(function() {
            document.getElementById("message-box").innerHTML = "Saving...";
            pageLoader.updateLocal(function() {
                pageLoader.sendData("/admin/save-data", function(data) {
                    document.getElementById("message-box").innerHTML = "Saved.";
                });
            });
        });
        
    },
    
    genPreview: function() {
        var newTab = window.open("/admin/preview-loading", "_blank");
        document.getElementById("message-box").innerHTML = "Uploading...";
        pageLoader.uploadImages(function() {
            document.getElementById("message-box").innerHTML = "Generating Preview...";
            pageLoader.updateLocal(function() {
                pageLoader.sendData("/admin/gen-preview", function(data) {
                    newTab.location = "/admin/preview/" + data["uid"].toString()
                    document.getElementById("message-box").innerHTML = "Preview generated.";
                });
            });
        });
    },
    
    sendData: function(url, success) {
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

            $.ajax({ url: $SCRIPT_ROOT + url,
                data: {
                    list_elements: JSON.stringify(tmpList),
                    static_elements: JSON.stringify(window.staticElements),
                    page_name: window.page
                },
                success: success,
                dataType: "json", type: "post"
            });
    }
    
};

$(document).ready(function() {
    init();
});