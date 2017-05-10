function makeTable(listName) {
    var lists = window.lists;
    var div = document.createElement("div");
    div.className = "list-selection";
    div.setAttribute("id", listName);
    var listDisplay = document.createTextNode(lists[listName]["_display"] + ":");
    
    document.getElementById("lists").appendChild(listDisplay)
    document.getElementById("lists").appendChild(div)
    
    for (var x = 0; x < lists[listName]["_count"]; x++) {
        var variables = {};
    
        for (var name in lists[listName]) {
            if (name.charAt(0) != "_") {
                variables[name] = {};
                variables[name]["display"] = lists[listName][name]["display"];
                variables[name]["type"] = lists[listName][name]["type"];
                variables[name]["data"] = lists[listName][name]["data"][x];
            }   
        }
            
            
        addItem(listName, variables, false, x+1);
    }
    
    var addNew = document.createElement("button");
    addNew.setAttribute("onclick", "addItemEmpty('" + listName + "')");
    addNew.appendChild(document.createTextNode("Add New"));
    document.getElementById("lists").appendChild(addNew);
    document.getElementById("lists").appendChild(document.createElement("br"));
    document.getElementById("lists").appendChild(document.createElement("br"));
}

function switchItems(listName, idA, idB) {
    var div = document.getElementById(listName);
    
    var a = div.getElementsByClassName(idA.toString())[0];
    var b = div.getElementsByClassName(idB.toString())[0];
        
    var areasB = b.getElementsByTagName("textarea");
    var areasA = a.getElementsByTagName("textarea");
    var dataB = []
    var dataA = []
    for (var x = 0; x < areasB.length; x++) {
        dataB[x] = areasB[x].value;
        dataA[x] = areasA[x].value;
    }

    areasA = a.getElementsByTagName("textarea");
    areasB = b.getElementsByTagName("textarea");
    for (var x = 0; x < areasB.length; x++) {
        areasA[x].value = dataB[x];
        areasB[x].value = dataA[x];
    }
}

function pushDown(listName, top) {
    var div = document.getElementById(listName);
    
    var lists = window.lists;
    var count = lists[listName]["_count"];
    
    for (var i = count - 1; i > top; i--) {
        switchItems(listName, i, i-1);
    }
    
    reorderList(listName);
}

function delItem(listName, id) {
    var lists = window.lists;
    var list = document.getElementById(listName);
    lists[listName]["_count"]--;
    
    var item = list.getElementsByClassName((id).toString())[0];
    list.removeChild(item);
    reorderList(listName);
}

function reorderList(listName) {
    var div = document.getElementById(listName);
    var items = div.getElementsByTagName("div");
    for (var i = 0; i < items.length; i++) {
        items[i].className = i.toString();
        items[i].getElementsByTagName("dt")[0].innerHTML = (i+1).toString();
        var buttons = items[i].getElementsByTagName("button")
        var patt = new RegExp("[0-9]+\\)");
        for (var x = 0; x < buttons.length; x++) {
            var click = buttons[x].getAttribute("onclick");
            buttons[x].setAttribute("onclick", click.replace(patt, i.toString() + ")"));
        }
    }
}

function addItem(listName, variables, isNew, num) {
    var lists = window.lists;
    var n;
    if (isNew) {
        lists[listName]["_count"]++;
        n = lists[listName]["_count"];
    } else {
        n = num;
    }
    var div = document.createElement("div");
    div.className = (n-1).toString();
    
    var dt = document.createElement("dt");
    var dd = document.createElement("dd");
    var table = document.createElement("table");
    var inner = document.createTextNode(n.toString());
    dt.appendChild(inner);
    for (var variable in variables) {
        var row = document.createElement("tr");
                
        var def = document.createElement("td");
        var data = document.createElement("td");
        
        console.log(variables[variable]["type"]);
        
        
        if (variables[variable]["type"] == "text") {
            var textarea = document.createElement("textarea");
            textarea.appendChild(document.createTextNode(variables[variable]["data"]));
            data.appendChild(textarea);
        } else if (variables[variable]["type"] == "image") {
            var form = document.createElement("form");
            form.className = "image-upload";
            form.setAttribute("enc-type", "multipart/form-data");
            var selector = document.createElement("input");
            selector.setAttribute("type", "file");
            selector.setAttribute("name", "file");
            var span = document.createElement("span");
            span.className = "progress";
            var placeholder = document.createElement("textarea");
            placeholder.className = "image-placeholder";
            form.appendChild(selector);
            form.appendChild(span);
            form.appendChild(placeholder);
            data.appendChild(form);
        }
                
        def.appendChild(document.createTextNode(variables[variable]["display"]));
                
        row.appendChild(def);
        row.appendChild(data);
        
        table.appendChild(row);
    }
    
    dd.appendChild(table);
    
    div.appendChild(dt);
    div.appendChild(dd);
    
    var insAbove = document.createElement("button");
    insAbove.appendChild(document.createTextNode("Insert above"));
    insAbove.setAttribute("onclick", "insertAbove('" + listName + "', " + (n-1).toString() + ")");
    var insBelow = document.createElement("button");
    insBelow.appendChild(document.createTextNode("Insert below"));
    insBelow.setAttribute("onclick", "insertBelow('" + listName + "', " + (n-1).toString() + ")");
    var moveUp = document.createElement("button");
    moveUp.appendChild(document.createTextNode("Move up"));
    moveUp.setAttribute("onclick", "moveUp('" + listName + "', " + (n-1).toString() + ")");
    var moveDown = document.createElement("button");
    moveDown.appendChild(document.createTextNode("Move down"));
    moveDown.setAttribute("onclick", "moveDown('" + listName + "', " + (n-1).toString() + ")");
    var del = document.createElement("button");
    del.appendChild(document.createTextNode("Delete"));
    del.setAttribute("onclick", "delItem('" + listName + "', " + (n-1).toString() + ")");
    
    div.appendChild(insAbove);
    div.appendChild(insBelow);
    div.appendChild(moveUp);
    div.appendChild(moveDown);
    div.appendChild(del);
    
    document.getElementById(listName).appendChild(div);
}

function addItemEmpty(listName) {
    var lists = window.lists;
    var variables = {};
    
    for (var name in lists[listName]) {
        if (name.charAt(0) != "_") {
            variables[name] = {};
            variables[name]["display"] = lists[listName][name]["display"];
            variables[name]["type"] = lists[listName][name]["type"];
            variables[name]["data"] = "";
        }   
    }
    
    addItem(listName, variables, true, 0);
} 

function insertItemEmpty(listName, top) {
    addItemEmpty(listName);
    pushDown(listName, top);
}

function insertAbove(listName, id) {
    insertItemEmpty(listName, id);
}

function insertBelow(listName, id) {
    insertItemEmpty(listName, id+1);
}

function moveUp(listName, id) {
    switchItems(listName, id, id-1);
}

function moveDown(listName, id) {
    switchItems(listName, id, id+1);
}

function start() {
    var lists = window.lists;
    
    for (var list in lists) {
        makeTable(list);
    }
}

function updateLocal() {
    var texts = window.texts;
    var lists = window.lists;
    var images = window.images;
    
    var textSection = document.getElementById("texts").getElementsByTagName("textarea");
    
    var k = 0;
    for (var text in texts) {
        texts[text]["data"] = textSection[k].value;
        console.log("test");
        k++;
    }
    
    var imageSection = document.getElementById("images").getElementsByTagName("textarea");
    
    k = 0;
    for (var image in images) {
        console.log(imageSection[k].value);
        images[image]["data"] = imageSection[k].value;
        k++;
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
    
}

function save(page) {
    if (confirm("Are you sure that you want to save? There is no way to revert after these changes are made.")) {
        uploadImages();
    }
}
    
function uploadImages() {
    var forms = document.getElementsByClassName("image-upload");
    document.getElementById("message-box").innerHTML = "Uploading (1/" + forms.length + ")...";
        
    for (var count = 0; count < forms.length; count++) {
        console.log(count)
        
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
                    console.log(data.filename);
                }
                
                if (i + 1 == forms.length) {
                    document.getElementById("message-box").innerHTML = "Saving...";
                    updateLocal();
                    saveData();
                } else {
                    document.getElementById("message-box").innerHTML = "Uploading Images (" + (i+1).toString() + "/" + forms.length.toString() + ")..."
                }
            }
        });
    
    }
}

function saveData() {
    var tmpList = {};
        for (var item in window.lists) {
            tmpList[item] = {};
            for (var variable in window.lists[item]) {
                if (variable.charAt(0) != "_") {
                    tmpList[item][variable] = window.lists[item][variable];
                }
            }
        }
        
        document.getElementById("message-box").innerHTML = "Saving...";
        
        console.log("one");
        $.ajax({ url: $SCRIPT_ROOT + "/admin/save-data",
            data: {
                list: JSON.stringify(tmpList),
                text: JSON.stringify(window.texts),
                image: JSON.stringify(window.images),
                page_name: window.page
            },
            success: function(data){
                document.getElementById("message-box").innerHTML = "Saved.";
            }, dataType: "json", type: "post"});
}