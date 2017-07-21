# Blackbox-tests Html-Image-Map-Creator (ENG)

| **Test nr.** | **Test case** | **Expected result** |
| --- | --- | --- |
| **1.** | (QGis.WKBPoint) The user exports all features in the zoomed "MapView" together with infobox and labels | Labels and infoboxes are displayed correctly in the generated HTML file |
| **2.** | (QGis.WKBPolygon) The user exports all features in the zoomed "MapView" together with infobox and labels | Labels and infoboxes are displayed correctly in the generated HTML file |
| **3.** | (QGis.WKBMultiPoint) The user exports all features in the zoomed "MapView" together with infobox and labels | Labels and infoboxes are displayed correctly in the generated HTML file |
| **4.** | (QGis.WKBMultiPolygon) The user exports all features in the zoomed "MapView" together with infobox and labels | Labels and infoboxes are displayed correctly in the generated HTML file |
| **5.** | The plugin is opened on an invalid geometry | Error message |
| **6.** | The plugin is opened on an empty layer | Error message |
| **7.** | The user specifies a filename and path where the files to be generated are found | The 3 files are exported with the user-selected name under the path specified by the user |
| **8.** | The user selects a positive offset for the label and the infobox | The label and infobox are moved downwards in the exported map |
| **9.** | The user selects a negative offset for the label and the infobox | The label and infobox are moved upwards in the exported map |
| **10.** | The user does not activate the checkbox for the label or for the infobox | The ok-button gets disabled (unclickable) |
| **11.** | The user activates the checkbox for the label but not for the infobox and starts the export | The export is succesful and only the labels for the POIs get displayed |
| **12.** | The user activates the checkbox for the infobox but not for the label and starts the export | The export is successfull and the POIs do not get labeled, an infobox opens if the POI is clicked |

| **Test nr.** | **Result** | **Comment** | **Success** |
| --- | --- | --- | --- |
| **1.** | Labels and infoboxes are displayed correctly in the generated HTML file | - | :+1: |
| **2.** | Labels and infoboxes are displayed correctly in the generated HTML file | - | :+1: |
| **3.** | Labels and infoboxes are displayed correctly in the generated HTML file | - | :+1: |
| **4.** | Labels and infoboxes are displayed correctly in the generated HTML file | - | :+1: |
| **5.** | Error message | - | :+1: |
| **6.** | Error message | - | :+1: |
| **7.** | The 3 files are exported with the user-selected name under the path specified by the user | - | :+1: |
| **8.** | The label and infobox are moved downwards in the exported map | - | :+1: |
| **9.** | The label and infobox are moved upwards in the exported map | - | :+1: |
| **10.** | The ok-button gets disabled (unclickable) | - | :+1: |
| **11.** | The export is succesful and only the labels for the POIs get displayed | - | :+1: |
| **12.** | The export is successfull and the POIs do not get labeled, an infobox opens if the POI is clicked | - | :+1: |
