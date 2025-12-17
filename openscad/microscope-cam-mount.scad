//printing stuff to fit on the microscope to hold the pizero and camera
//designed to fit in the arm of a microscope above the stage behind the optics
//will have to also allow for power cables to the existing lighting and power to the usb cam 

$fn=360;

//intersection(){
//#translate([-10,-10,-4]) cube([20,50,8]);
union(){
    //first test print of cross beam to fit in the arm and be screwed in place
    wiggle = 0.01;
    crossBeam = [17, 7, 51.25] ;
    screwOffset = [3.6, 3.5, -wiggle/2] ;
    screwD = 3.2 ;
    difference(){
        translate([-10,0,0]) cube(crossBeam);
        translate(screwOffset) cylinder(h = crossBeam.z + wiggle, d = screwD);
    }
    plateT = 3;
    overhang = 5;
    difference(){
        translate([-10,0,-overhang/2]) cube([plateT,37,crossBeam.z+overhang]);
        translate([-20,17.5,2*(crossBeam.z/3)])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        translate([-20,17.5,crossBeam.z/3])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = screwD);
        translate([-20,35,crossBeam.z/2])rotate([0,90,0])cylinder(h = crossBeam.z + wiggle, d = 15);
    }
}
//}