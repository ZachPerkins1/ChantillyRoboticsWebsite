function makeTable(listName) {
    var lists = window.lists;

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
}

function addItem(listName, variables, isNew, num) {
    var lists = window.lists
    var n;
    if (isNew) {
        lists[listName]["_count"]++;
        n = lists[listName]["_count"];
    } else {
        n = num;
    }
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
    
    document.getElementById(listName).appendChild(dt);
    document.getElementById(listName).appendChild(dd);
}


function start() {
    makeTable("mentors")
}