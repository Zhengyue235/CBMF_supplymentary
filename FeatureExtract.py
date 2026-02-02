import arcpy
from arcpy import env
from arcpy.sa import *
import os
import numpy as np

import arcpy

arcpy.CheckOutExtension("Spatial")
workpath="E:\\ChinaBuildingType\\"
arcpy.env.workspace=workpath
skip_list = [""]

fcs = arcpy.ListFeatureClasses()
for fc in fcs:
   Area = fc
   if Area in skip_list:
       print(Area)
   #########储存water等数据的位置
       building_data=workpath+Area
       Direction="F:\\osm\\Asia\\China\\"
       CityCenter=Direction+"China_osm_places_free_1.shp"
       water=Direction+"China_osm_water_free_1.shp"
       road=Direction+"China.gdb\\China_osm_road_free_1"
       #########储存导出的Point数据的位置
       point="E:\\ChinaBuildingType\\Points.gdb\\"+Area+ "_point"
       
       arcpy.RepairGeometry_management(in_features=building_data, delete_null="DELETE_NULL")
       arcpy.DeleteField_management(in_table=building_data, drop_field="ID")
       arcpy.DeleteIdentical_management(in_dataset=building_data, fields="Shape", xy_tolerance="", z_tolerance="0")
       arcpy.AddGeometryAttributes_management(building_data, "AREA_GEODESIC;PERIMETER_LENGTH_GEODESIC;POINT_COUNT", "METERS", "SQUARE_METERS", "")
       arcpy.AddField_management(building_data, "ID", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.CalculateField_management(in_table=building_data, field="ID", expression=" [OBJECTID]+20000000", expression_type="VB", code_block="")

    ###################################################NEAR
       arcpy.FeatureToPoint_management(in_features=building_data, out_feature_class=point, point_location="INSIDE")
       arcpy.AddField_management(point, "Compact", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "CookeJC", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "Fractality", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "SurfaceA", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "Compact3D", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "ShapeIndex", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "Volume", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "HeightCoef", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.CalculateField_management(in_table=point, field="HeightCoef", expression=" [Height]/[AREA_GEO]", expression_type="VB", code_block="")
       arcpy.CalculateField_management(in_table=point, field="Volume", expression=" [Height]*[AREA_GEO]", expression_type="VB", code_block="")
       arcpy.CalculateField_management(in_table=point, field="SurfaceA", expression=" [AREA_GEO]+([Height]*[PERIM_GEO])", expression_type="VB", code_block="")
       arcpy.CalculateField_management(in_table=point, field="Compact3D", expression=" [Volume]/([Height]*[PERIM_GEO])", expression_type="VB", code_block="")
       arcpy.CalculateField_management(in_table=point, field="ShapeIndex", expression=" [SurfaceA]/[Volume]", expression_type="VB", code_block="")
       arcpy.CalculateField_management(point, "Compact", "(4*3.1415926*!AREA_GEO!/(!PERIM_GEO!*!PERIM_GEO!))", "PYTHON_9.3", "")
       arcpy.CalculateField_management(point, "Fractality", "1-0.5*(Log ( [AREA_GEO] )/Log ( [PERIM_GEO] ))", "VB", "")
       arcpy.CalculateField_management(point, "CookeJC", "([PERIM_GEO] /(4*Sqr ( [AREA_GEO] )))-1", "VB", "")
       arcpy.AddField_management(point, "DisCity", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "DisRoad", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "DisWater", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.AddField_management(point, "DisBuildig", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
       arcpy.Near_analysis(in_features=point, near_features=water, search_radius="", location="NO_LOCATION", angle="NO_ANGLE", method="GEODESIC")
       arcpy.CalculateField_management(in_table=point, field="DisWater", expression=" [NEAR_DIST]", expression_type="VB", code_block="")
       arcpy.Near_analysis(in_features=point, near_features=CityCenter, search_radius="", location="NO_LOCATION", angle="NO_ANGLE", method="GEODESIC")
       arcpy.CalculateField_management(in_table=point, field="DisCity", expression=" [NEAR_DIST]", expression_type="VB", code_block="")
       arcpy.Near_analysis(in_features=point, near_features=road, search_radius="", location="NO_LOCATION", angle="NO_ANGLE", method="GEODESIC")
       arcpy.CalculateField_management(in_table=point, field="DisRoad", expression=" [NEAR_DIST]", expression_type="VB", code_block="")
       arcpy.Near_analysis(in_features=point, near_features=point, search_radius="", location="NO_LOCATION", angle="NO_ANGLE", method="GEODESIC")
       arcpy.CalculateField_management(in_table=point, field="DisBuildig", expression=" [NEAR_DIST]", expression_type="VB", code_block="")
       arcpy.DeleteField_management(in_table=point, drop_field="NEAR_FID;NEAR_DIST")
       arcpy.AddGeometryAttributes_management(point, "POINT_X_Y_Z_M", "", "", "")

 #####################################################poi3
workpath="E:\\ChinaBuildingType\\kernel2\\"
poi="E:\\ChinaBuildingType\\POI.gdb\\POI"
boundary="E:\\UrbanVillage\\boundary\\Jiangsu.shp"


i="Urban vilage"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=1")
arcpy.SelectLayerByLocation_management("lyr"+i, "INTERSECT", boundary, selection_type="SUBSET_SELECTION")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Subdnsion"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=2")
arcpy.SelectLayerByLocation_management("lyr"+i, "INTERSECT", boundary, selection_type="SUBSET_SELECTION")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Hotel"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=3")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Restaurant"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=4")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Factory"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=5")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Pubic"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=6")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Transport"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=7")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Business"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=8")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Commercral"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=9")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="School"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=10")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Hoptal"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=11")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

i="Govement"
print(i)
arcpy.MakeFeatureLayer_management(poi ,"lyr"+i)
arcpy.SelectLayerByAttribute_management ("lyr"+i, "NEW_SELECTION", "classify=12")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('WGS 1984 UTM Zone 49N')
arcpy.env.extent = (boundary)
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_500.tif", "30", "500", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_1000.tif", "30", "1000", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("lyr"+i, "NONE", workpath+i+"_100.tif", "30", "100", "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")

workpath="E:\\ChinaBuildingType\\Points.gdb\\"
arcpy.env.workspace=workpath
fcs = arcpy.ListFeatureClasses()
for fc in fcs:
    print(fc)
    if fc.lower() in north_list: 
        print(fc)
        inPointFeatures = fc
        inRasterList = [
            ["E:/UrbanVillage/POI/pois/Factory_100.tif", "Factory_100"], 
            ["E:/UrbanVillage/POI/pois/Govement_100.tif", "Govement_100"], 
            ["E:/UrbanVillage/POI/pois/Hoptal_100.tif", "Hoptal_100"], 
            ["E:/UrbanVillage/POI/pois/Hotel_100.tif", "Hotel_100"], 
            ["E:/UrbanVillage/POI/pois/Pubic_100.tif", "Pubic_100"],
            ["E:/UrbanVillage/POI/pois/Restaurant_100.tif ", "Restaurant_100"],
            ["D:/School_100.tif", "School_100"], 
            ["C:/southwest/Subdnsion_100.tif", "Subdnsion_100"], 
            ["E:/UrbanVillage/POI/pois/Transport_100.tif", "Transport_100"], 
            ["D:/Urban vilage_100.tif", "Urbanvilage_100"], 
            ["D:/Commercral_100.tif", "Commercral_100"],
            ["D:/Business_100.tif", "Business_100"], 
        ]
        arcpy.CheckOutExtension("Spatial")
        ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")
    else:
        print("Skipping "+fc)
