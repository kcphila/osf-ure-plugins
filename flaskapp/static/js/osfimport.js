$(document).ready(function () {

});
function import_to_osf(){

    var wait_dialog = $('#wait-dialog');
    $('#wait-dialog').dialog('open');
    osf.local(
        '/import/docx',
        $('#document-import').serialize(),
        show_import_results,
        function(data){
            $('#wait-dialog').dialog("close");
            ureAjaxError(data);
        }
    );
}

function show_import_results(data){
    $('#wait-dialog').dialog("close");
    
    console.log(data);
    $('#result-header').html('<h1>Import Complete</h1><p><a href="http://osf.io/'+data.rootnodeid+'/">Click Here</a> to leave the importer and go to the '+data.rootnodename+' Project.</p><a href="/">Click Here</a> to return to the URE Methods extensions index.</p><p class="help-text">Below is a list of completed actions. Click on the links to open a <i>new window</i> for the page.</p><p>If you accidentally overwrote a wiki page, you can <b>revert</b> it to the old <b>Version</b> via the wiki page. If you accidentally deleted a wiki or component, it cannot be recovered.<b><i>TODO: Verify no recovery</b></i></p>')
    var div = $('<div></div>');

    ['ignored', 'deleted', 'updated', 'created'].forEach(function(type){
        var actions = data.componentactions[type];
        if(actions && actions.length){
            div.append('<h2>Components ' + type[0].toUpperCase() + type.slice(1)+ '</h2>');
            var ul = div.append('<ul></ul>');
            actions.forEach(function(comp){
                var text = comp[1];
                if(comp.length >= 3) // Optional 3rd element is a message to append
                    text += '. <div class="help-text">'+comp[2]+'</div>'
                if(type == 'deleted') //no link
                    ul.append('<li>' + text + '</li>')
                else ul.append('<li><a href="http://osf.io/'+comp[0]+'/" target="_blank">' + text + '</a></li>')
            });
        }
    });

    ['ignored', 'deleted',  'updated', 'created'].forEach(function(type){
        var actions = data.wikiactions[type];
        if(actions && actions.length){
            div.append('<h2>Wikis ' + type[0].toUpperCase() + type.slice(1)+ '</h2>');
            var ul = div.append('<ul></ul>')
            actions.forEach(function(comp){
                if(type == 'deleted')
                    ul.append('<li>' + comp[1] + ' from Node <a href="http://osf.io/'+comp[2]+'/" target="_blank">'+data.nodemap[comp[0]]+ '</li>')
                else ul.append('<li><a href="http://osf.io/'+comp[0]+'/wiki/'+encodeURIComponent(comp[1])+'/" target="_blank">' + comp[1] + '</a> from Node <a href="http://osf.io/'+comp[2]+'/" target="_blank">'+data.nodemap[comp[0]]+ '</li>')
            });
        }
    });
    $('#result-message').html(div)
    $('#result-dialog').dialog('open');
    console.log(data)
    console.log("Import complete")

}