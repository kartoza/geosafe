/**
 This script is used for common js function in geosafe/analysis module
 **/

/**
 * Function to toggle saving behaviour of analysis result
 *
 * If not saved, then a daily task will delete it
 * This script is used in conjunction with this widget called onoffswitch:
 * https://proto.io/freebies/onoff/
 * @param id
 */
function toggle_analysis_saved(url, id){
    url = url.replace("-1", id);
    var $checkbox = $(".save-analysis input[data-id='"+id+"']");
    $checkbox.parent().addClass("processing");
    $checkbox.prop("disabled", true);
    $.post(url, function(data){
        if(data && data.success){
            $checkbox.parent().removeClass("processing");
            $checkbox.prop("checked", data.is_saved);
            $checkbox.prop("disabled", false);
        }
    });
}
