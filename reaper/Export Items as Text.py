# Export Items as Text.py
# (c) 2021 Jamie Hardt. All rights reserved.
#
#

import json
import os.path
import datetime

item_records = list()

for i in range(0, RPR_CountMediaItems(0) ):
    this_item = RPR_GetMediaItem(0, i)

    item_record = {}
    item_record["mute"] = True if RPR_GetMediaItemInfo_Value(this_item, "B_MUTE_ACTUAL") > 0. else False
    
    item_record["duration"] = RPR_GetMediaItemInfo_Value(this_item, "D_LENGTH")
    _, item_record["duration_tc"], _, _, _ = RPR_format_timestr_len(item_record["duration"], "", 128, 0., 5)

    item_record["position"] = RPR_GetMediaItemInfo_Value(this_item, "D_POSITION")
    _, item_record["position_tc"], _, _ = RPR_format_timestr_pos(item_record["position"], "", 128, 5)

    item_record["selected"] = True if RPR_GetMediaItemInfo_Value(this_item, "B_UISEL") > 0. else False
    _, _, _, item_record["notes"], _ = RPR_GetSetMediaItemInfo_String(this_item, "P_NOTES", "", False)
    _, _, _, item_record["item_guid"], _ = RPR_GetSetMediaItemInfo_String(this_item, "GUID", "", False)

    active_take = RPR_GetActiveTake(this_item)
    _, _, _, item_record["active_take_name"], _ = RPR_GetSetMediaItemTakeInfo_String(active_take, "P_NAME", "", False)  
    _, _, _, item_record["active_take_guid"], _ = RPR_GetSetMediaItemTakeInfo_String(active_take, "GUID", "", False) 

    item_track = RPR_GetMediaItemTrack(this_item)
    _, _, _, item_record["track_name"], _ = RPR_GetSetMediaTrackInfo_String(item_track, "P_NAME", "", False)
    _, _, _, item_record["track_guid"], _ = RPR_GetSetMediaTrackInfo_String(item_track, "GUID", "", False)
    item_record["track_index"] = RPR_GetMediaTrackInfo_Value(item_track, "IP_TRACKNUMBER")
    item_record["track_muted"] = True if RPR_GetMediaTrackInfo_Value(item_track, "B_MUTE") > 0. else False

    item_records = item_records + [item_record]

output = dict()
output["items"] = item_records
_, output["project_title"], _ = RPR_GetProjectName(0, "", 1024)
_, _, output["project_author"], _ = RPR_GetSetProjectAuthor(0, False, "", 1024)
output["project_frame_rate"], _, output["project_drop_frame"] = RPR_TimeMap_curFrameRate(0, True)

output_path, _ = RPR_GetProjectPath("", 1024)

now = datetime.datetime.now()
output_title = output["project_title"]

if output_title == "":
    output_title = "unsaved project"

output_file_name = "%s Text Export %s.txt" % (output_title, now.strftime('%Y%m%d_%H%M')) 
output_path = output_path + "/" + output_file_name

with open(output_path, "w") as f:
    json.dump(output, f, allow_nan=True, indent=4)

RPR_ShowMessageBox("Exported text file \"%s\" to project folder." % output_file_name, "Text Export Complete", 0)

#RPR_ShowConsoleMsg(output_path)