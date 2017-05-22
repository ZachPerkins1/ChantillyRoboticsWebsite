var listLoader = {

    makeTable: function(listName) {
        var lists = window.listElements;
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
                
                
            listLoader.addItem(listName, variables, false, x+1);
        }
        
        var addNew = document.createElement("button");
        addNew.setAttribute("onclick", "listLoader.addItemEmpty('" + listName + "')");
        addNew.appendChild(document.createTextNode("Add New"));
        document.getElementById("lists").appendChild(addNew);
        document.getElementById("lists").appendChild(document.createElement("br"));
        document.getElementById("lists").appendChild(document.createElement("br"));
    },
    
    switchItems: function(listName, idA, idB) {
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
    },
    
    pushDown: function(listName, top) {
        var div = document.getElementById(listName);
        
        var lists = window.listElements;
        var count = lists[listName]["_count"];
        
        for (var i = count - 1; i > top; i--) {
            listLoader.switchItems(listName, i, i-1);
        }
        
        listLoader.reorderList(listName);
    },
    
    delItem: function(listName, id) {
        var lists = window.listElements;
        var list = document.getElementById(listName);
        lists[listName]["_count"]--;
        
        var item = list.getElementsByClassName((id).toString())[0];
        list.removeChild(item);
        listLoader.reorderList(listName);
    },
    
    reorderList: function(listName) {
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
    },
    
    addItem: function(listName, variables, isNew, num) {
        var lists = window.listElements;
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
            
            data.className = "item-content";
            
            fillContent(variables[variable]["type"], data, variables[variable]);
            
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
        insAbove.setAttribute("onclick", "listLoader.insertAbove('" + listName + "', " + (n-1).toString() + ")");
        var insBelow = document.createElement("button");
        insBelow.appendChild(document.createTextNode("Insert below"));
        insBelow.setAttribute("onclick", "listLoader.insertBelow('" + listName + "', " + (n-1).toString() + ")");
        var moveUp = document.createElement("button");
        moveUp.appendChild(document.createTextNode("Move up"));
        moveUp.setAttribute("onclick", "listLoader.moveUp('" + listName + "', " + (n-1).toString() + ")");
        var moveDown = document.createElement("button");
        moveDown.appendChild(document.createTextNode("Move down"));
        moveDown.setAttribute("onclick", "listLoader.moveDown('" + listName + "', " + (n-1).toString() + ")");
        var del = document.createElement("button");
        del.appendChild(document.createTextNode("Delete"));
        del.setAttribute("onclick", "listLoader.delItem('" + listName + "', " + (n-1).toString() + ")");
        
        div.appendChild(insAbove);
        div.appendChild(insBelow);
        div.appendChild(moveUp);
        div.appendChild(moveDown);
        div.appendChild(del);
        
        document.getElementById(listName).appendChild(div);
    },
    
    addItemEmpty: function(listName) {
        var lists = window.listElements;
        var variables = {};
        
        for (var name in lists[listName]) {
            if (name.charAt(0) != "_") {
                variables[name] = {};
                variables[name]["display"] = lists[listName][name]["display"];
                variables[name]["type"] = lists[listName][name]["type"];
                variables[name]["data"] = clone(window.typeInfo[lists[listName][name]["type"]]["empty"]);
                console.log(variables[name]["data"]);
            }   
        }
        
        listLoader.addItem(listName, variables, true, 0);
    },
    
    insertItemEmpty: function(listName, top) {
        listLoader.addItemEmpty(listName);
        listLoader.pushDown(listName, top);
    },
    
    insertAbove: function(listName, id) {
        listLoader.insertItemEmpty(listName, id);
    },
    
    insertBelow: function(listName, id) {
        listLoader.insertItemEmpty(listName, id+1);
    },
    
    moveUp: function(listName, id) {
        listLoader.switchItems(listName, id, id-1);
    },
    
    moveDown: function(listName, id) {
        listLoader.switchItems(listName, id, id+1);
    }
};

function clone(obj) {
    var copy;
 
    if (null == obj || "object" != typeof obj) return obj;
 
    if (obj instanceof Date) {
        copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }
 
    if (obj instanceof Array) {
        copy = [];
        for (var i = 0, len = obj.length; i < len; i++) {
            copy[i] = clone(obj[i]);
        }
        return copy;
    }
 
    if (obj instanceof Object) {
        copy = {};
        for (var attr in obj) {
            if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
        }
        return copy;
    }
 
    throw new Error("Unable to copy obj! Its type isn't supported.");
}
