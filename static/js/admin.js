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
        var textarea = document.createElement("textarea");
        textarea.appendChild(document.createTextNode(variables[variable]["data"]));
                
        var def = document.createElement("td");
        var data = document.createElement("td");
                
        data.appendChild(textarea);
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
    
    var textSection = document.getElementById("texts").getElementsByTagName("textarea");
    
    var k = 0;
    for (var text in texts) {
        texts[text]["data"] = textSection[k].value;
        k++;
    } 
    
    var listSection = document.getElementById("lists");
    for (var i = 0; i < lists.length; i++) {
        var divs = listSection[i].getElementsByTagName["div"];
    
        for (var variable in lists) {
            var x = 0;
            var div = listSection[i];
            
            if (variable.charAt(0) != "_") {
                lists[variable]["data"].clear();
                for (var item in divs) {
                    var inputs = item.getElementsByTagName("textarea");
                    lists[variable]["data"].push(inputs[x]);
                }
                x++;
            }
        }
    }
    
    for (var text in texts) {
        console.log(texts[text]["data"]);
    }
    
    
}

function save() {
    if (confirm("Are you sure that you want to save? There is no way to revert after these changes are made.")) {
        updateLocal();
        
        var tmpList = {};
        for (var item in window.lists) {
            if (item.charAt(0) != "_") {
                tmpList[item] = window.lists[item];
            }
        }
        
        $.ajax({ url: $SCRIPT_ROOT + "/admin/save-data",
            data: {
                lists: JSON.stringify(tmpList),
                texts: JSON.stringify(window.texts),
                page_name: "about-us",
                test: "hello"
            },
            success: function(data){
                alert(data.data);
            }, dataType: "json", type: "post"});
    }
}