
function del(id) {
    $.ajax({ url: $SCRIPT_ROOT + url,
        data: {
            uid: id
        },
                
    dataType: "json", type: "post"
    });
}