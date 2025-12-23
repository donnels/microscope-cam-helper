//printing stuff to fit on the microscope to hold the pizero and camera
//designed to fit in the arm of a microscope above the stage behind the optics
//will have to also allow for power cables to the existing lighting and power to the usb cam 

$fn=100;

//intersection(){
//#translate([-10,-10,-4]) cube([20,50,8]);
    wiggle = 0.01;
    crossBeam = [17, 7, 51.25] ;
    screwOffset = [3.6, 3.5, -wiggle/2] ;
    heatInsertD = 3.2 ;
    screwD = 2.5 ;
    screwHeadD = 4.5 ;
    plateT = 4;
    overhang = 5;

union(){
    //first test print of cross beam to fit in the arm and be screwed in place
    difference(){
        translate([-10,0,0]) cube(crossBeam);
        translate(screwOffset) cylinder(h = crossBeam.z + wiggle, d = heatInsertD);
    }
    difference(){
        //mount plate
        translate([-11,0,-overhang/2]) cube([plateT,37,crossBeam.z+overhang]);
        //heat inserts
        translate([-20,17.5,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = heatInsertD);
        translate([-20,17.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = heatInsertD);
        //screw holes
        translate([-20,10,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        translate([-20,10.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        //scew heads
        translate([-18.5,10,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = 10, d = screwHeadD);
        translate([-18.5,10.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = 10, d = screwHeadD);
        //Cable path
        translate([-20,35,crossBeam.z/2])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = 15);
    }
}
//}
translate([-20.0,0]) union(){
    difference(){
        //mount plate
        translate([-11,0,-overhang/2]) cube([plateT,37,crossBeam.z+overhang]);
        //screw holes
        translate([-20,17.5,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        translate([-20,17.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        //scew heads
        translate([-20,17.5,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = 10, d = screwHeadD);
        translate([-20,17.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = 10, d = screwHeadD);
        //Cable path
        translate([-20,35,crossBeam.z/2])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = 15);

    }
}