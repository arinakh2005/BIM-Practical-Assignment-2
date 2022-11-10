import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate

from StdReinfShapeBuilder.RotationAngles import RotationAngles
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from HandleService import HandleService


def check_allplan_version(build_ele, version):
    
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = BridgeGirder(doc)

    return element.create(build_ele)


def modify_element_property(build_ele, name, value):
    if (name == "GirderHeight"):
        change = value - build_ele.HeightUpperShelf.value - build_ele.RibHeight.value - build_ele.HeightLowerShelf2.value - build_ele.HeightLowerShelf.value
        print(change)
        if (change < 0):
            change = abs(change)
            if (build_ele.HeightUpperShelf.value > 330.):
                if (build_ele.HeightUpperShelf.value - change < 330.):
                    change -= build_ele.HeightUpperShelf.value - 330.
                    build_ele.HeightUpperShelf.value = 330.
                else:
                    build_ele.HeightUpperShelf.value -= change
                    change = 0.
            if (change != 0) and (build_ele.HeightLowerShelf2.value > 170.):
                if (build_ele.HeightLowerShelf2.value - change < 170.):
                    change -= build_ele.HeightLowerShelf2.value - 170.
                    build_ele.HeightLowerShelf2.value = 170.
                else:
                    build_ele.HeightLowerShelf2.value -= change
                    change = 0.
            if (change != 0) and (build_ele.HeightLowerShelf.value > 160.):
                if (build_ele.HeightLowerShelf.value - change < 160.):
                    change -= build_ele.HeightLowerShelf.value - 160.
                    build_ele.HeightLowerShelf.value = 160.
                else:
                    build_ele.HeightLowerShelf.value -= change
                    change = 0.
            if (change != 0) and (build_ele.RibHeight.value > 475.):
                if (build_ele.RibHeight.value - change < 475.):
                    change -= build_ele.RibHeight.value - 475.
                    build_ele.RibHeight.value = 475.
                else:
                    build_ele.RibHeight.value -= change
                    change = 0.
        else:
            build_ele.RibHeight.value += change
        if (value - build_ele.HeightUpperShelf.value - 45.5 < build_ele.HoleHeight.value):
            build_ele.HoleHeight.value = value - build_ele.HeightUpperShelf.value - 45.5   
    elif (name == "HeightUpperShelf"):
        build_ele.GirderHeight.value = value + build_ele.RibHeight.value + build_ele.HeightLowerShelf2.value + build_ele.HeightLowerShelf.value
    elif (name == "RibHeight"):
        build_ele.GirderHeight.value = value + build_ele.HeightUpperShelf.value + build_ele.HeightLowerShelf2.value + build_ele.HeightLowerShelf.value
    elif (name == "HeightLowerShelf2"):
        build_ele.GirderHeight.value = value + build_ele.HeightUpperShelf.value + build_ele.RibHeight.value + build_ele.HeightLowerShelf.value
        if (value + build_ele.HeightLowerShelf.value + 45.5 > build_ele.HoleHeight.value):
            build_ele.HoleHeight.value = value + build_ele.HeightLowerShelf.value + 45.5
    elif (name == "HeightLowerShelf"):
        build_ele.GirderHeight.value = value + build_ele.HeightUpperShelf.value + build_ele.RibHeight.value + build_ele.HeightLowerShelf2.value
        if (build_ele.HeightLowerShelf2.value + value + 45.5 > build_ele.HoleHeight.value):
            build_ele.HoleHeight.value = build_ele.HeightLowerShelf2.value + value + 45.5
    elif (name == "HoleHeight"):
        if (value > build_ele.GirderHeight.value - build_ele.HeightUpperShelf.value - 45.5):
            build_ele.HoleHeight.value = build_ele.GirderHeight.value - build_ele.HeightUpperShelf.value - 45.5
        elif (value < build_ele.HeightLowerShelf.value + build_ele.HeightLowerShelf2.value + 45.5):
            build_ele.HoleHeight.value = build_ele.HeightLowerShelf.value + build_ele.HeightLowerShelf2.value + 45.5
    elif (name == "HoleDepth"):
        if (value >= build_ele.GirderLength.value / 2.):
            build_ele.HoleDepth.value = build_ele.GirderLength.value / 2. - 45.5

    return True


def move_handle(build_ele, handle_prop, input_pnt, doc):
    build_ele.change_property(handle_prop, input_pnt)

    if (handle_prop.handle_id == "GirderHeight"):
        build_ele.RibHeight.value = build_ele.GirderHeight.value - build_ele.HeightUpperShelf.value - build_ele.HeightLowerShelf.value - build_ele.HeightLowerShelf2.value
        if (build_ele.HoleHeight.value > build_ele.GirderHeight.value - build_ele.HeightUpperShelf.value - 45.5):
            build_ele.HoleHeight.value = build_ele.GirderHeight.value - build_ele.HeightUpperShelf.value - 45.5

    return create_element(build_ele, doc)

class BridgeGirder():

    def __init__(self, doc):

        self.model_ele_list = []
        self.handle_list = []
        self.document = doc
        
    def create(self, build_ele):
        
        self._width_upper_shelf = build_ele.WidthUpperShelf.value
        self._height_upper_shelf = build_ele.HeightUpperShelf.value

        self._width_lower_shelf = build_ele.WidthLowerShelf.value
        self._height_lower_shelf_2 = build_ele.HeightLowerShelf2.value
        self._height_lower_shelf = build_ele.HeightLowerShelf.value
        self._bot_sh_height = self._height_lower_shelf_2 + self._height_lower_shelf

        if (build_ele.RibThick.value > min(self._width_upper_shelf, self._width_lower_shelf)):
            build_ele.RibThick.value = min(self._width_upper_shelf, self._width_lower_shelf)        
        self._rib_thickness = build_ele.RibThick.value
        self._rib_height = build_ele.RibHeight.value

        self._girder_length = build_ele.GirderLength.value
        self._girder_width = max(self._width_upper_shelf, self._width_lower_shelf)
        self._girder_height = build_ele.GirderHeight.value

        self._hole_depth = build_ele.HoleDepth.value
        self._hole_height = build_ele.HoleHeight.value

        self._angleX = build_ele.RotationAngleX.value
        self._angleY = build_ele.RotationAngleY.value
        self._angleZ = build_ele.RotationAngleZ.value

        self.create_girder(build_ele)
        self.create_handles(build_ele)
        
        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), self._angleX, self._angleY, self._angleZ, self.model_ele_list)

        rot_angles = RotationAngles(self._angleX, self._angleY, self._angleZ)
        HandleService.transform_handles(self.handle_list, rot_angles.get_rotation_matrix())
        
        return (self.model_ele_list, self.handle_list)


    def create_girder(self, build_ele):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Stroke = 1

        bottom_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._girder_width - self._width_lower_shelf) / 2., 0., 0.), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._width_lower_shelf, self._girder_length, self._bot_sh_height)

        edges = AllplanUtil.VecSizeTList()
        edges.append(10)
        edges.append(8)
        err, bottom_shelf = AllplanGeo.ChamferCalculus.Calculate(bottom_shelf, edges, 20., False)

        top_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._girder_width - self._width_upper_shelf) / 2., 0., self._girder_height - self._height_upper_shelf), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._width_upper_shelf, self._girder_length, self._height_upper_shelf)

        top_shelf_notch = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._girder_width - self._width_upper_shelf) / 2., 0., self._girder_height - 45.), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), 60., self._girder_length, 45.)
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        top_shelf_notch = AllplanGeo.Move(top_shelf_notch, AllplanGeo.Vector3D(self._width_upper_shelf - 60., 0, 0))
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        
        err, girder = AllplanGeo.MakeUnion(bottom_shelf, top_shelf)
        if not GeometryValidate.polyhedron(err):
            return

        rib = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0., 0., self._bot_sh_height), AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._girder_width, self._girder_length, self._rib_height)
        
        err, girder = AllplanGeo.MakeUnion(girder, rib)
        if not GeometryValidate.polyhedron(err):
            return
        
        left_notch_pol = AllplanGeo.Polygon2D()
        left_notch_pol += AllplanGeo.Point2D((self._girder_width - self._rib_thickness) / 2., self._girder_height - self._height_upper_shelf)
        left_notch_pol += AllplanGeo.Point2D((self._girder_width - self._rib_thickness) / 2., self._bot_sh_height)
        left_notch_pol += AllplanGeo.Point2D((self._girder_width - self._width_lower_shelf) / 2., self._height_lower_shelf)
        left_notch_pol += AllplanGeo.Point2D(0., self._height_lower_shelf)     
        left_notch_pol += AllplanGeo.Point2D(0., self._girder_height - 100.)
        left_notch_pol += AllplanGeo.Point2D(0., self._girder_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._girder_width - self._width_upper_shelf) / 2., self._girder_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._girder_width - self._rib_thickness) / 2., self._girder_height - self._height_upper_shelf)
        if not GeometryValidate.is_valid(left_notch_pol):
            return
        
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 0, 0)
        path += AllplanGeo.Point3D(0, build_ele.GirderLength.value, 0)

        err, notches = AllplanGeo.CreatePolyhedron(left_notch_pol, AllplanGeo.Point2D(0., 0.), path)
        if GeometryValidate.polyhedron(err):
            edges = AllplanUtil.VecSizeTList()
            if (self._rib_thickness == self._width_lower_shelf):
                edges.append(0)
            elif (self._rib_thickness == self._width_upper_shelf):
                edges.append(1)
            else:
                edges.append(0)
                edges.append(2)
            err, notches = AllplanGeo.FilletCalculus3D.Calculate(notches, edges, 100., False)

            plane = AllplanGeo.Plane3D(AllplanGeo.Point3D(self._girder_width / 2., 0, 0), AllplanGeo.Vector3D(1, 0, 0))
            right_notch = AllplanGeo.Mirror(notches, plane)

            err, notches = AllplanGeo.MakeUnion(notches, right_notch)
            if not GeometryValidate.polyhedron(err):
                return
            
            err, girder = AllplanGeo.MakeSubtraction(girder, notches)
            if not GeometryValidate.polyhedron(err):
                return

        sling_holes = AllplanGeo.BRep3D.CreateCylinder(AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0,build_ele.HoleDepth.value, build_ele.HoleHeight.value), AllplanGeo.Vector3D(0, 0, 1), AllplanGeo.Vector3D(1, 0, 0)), 45.5, self._girder_width)
        
        sling_hole_moved = AllplanGeo.Move(sling_holes, AllplanGeo.Vector3D(0., self._girder_length - self._hole_depth * 2, 0))

        err, sling_holes = AllplanGeo.MakeUnion(sling_holes, sling_hole_moved)
        if not GeometryValidate.polyhedron(err):
            return
            
        err, girder = AllplanGeo.MakeSubtraction(girder, sling_holes)
        if not GeometryValidate.polyhedron(err):
            return

        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(com_prop, girder))
        

    def create_handles(self, build_ele):
        handle1 = HandleProperties("GirderLength",
                                   AllplanGeo.Point3D(0., self._girder_length, 0.),
                                   AllplanGeo.Point3D(0, 0, 0),
                                   [("GirderLength", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle1)

        handle2 = HandleProperties("GirderHeight",
                                   AllplanGeo.Point3D(0., 0., self._girder_height),
                                   AllplanGeo.Point3D(0, 0, 0),
                                   [("GirderHeight", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle2)
        
        handle3 = HandleProperties("WidthUpperShelf",
                                   AllplanGeo.Point3D((self._girder_width - self._width_upper_shelf) / 2. + self._width_upper_shelf, 0., self._girder_height - 45.),
                                   AllplanGeo.Point3D((self._girder_width - self._width_upper_shelf) / 2., 0, self._girder_height - 45.),
                                   [("WidthUpperShelf", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle3)

        handle4 = HandleProperties("WidthLowerShelf",
                                   AllplanGeo.Point3D((self._girder_width - self._width_lower_shelf) / 2. + self._width_lower_shelf, 0., self._height_lower_shelf),
                                   AllplanGeo.Point3D((self._girder_width - self._width_lower_shelf) / 2., 0, self._height_lower_shelf),
                                   [("WidthLowerShelf", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle4)
        
        handle5 = HandleProperties("RibThick",
                                   AllplanGeo.Point3D((self._girder_width - self._rib_thickness) / 2. + self._rib_thickness, 0., self._girder_height / 2.),
                                   AllplanGeo.Point3D((self._girder_width - self._rib_thickness) / 2., 0, self._girder_height / 2.),
                                   [("RibThick", HandleDirection.point_dir)],
                                   HandleDirection.point_dir, True)
        self.handle_list.append(handle5)