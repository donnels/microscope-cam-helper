//printing stuff to fit on the microscope to hold the pizero and camera
//designed to fit in the arm of a microscope above the stage behind the optics
//will have to also allow for power cables to the existing lighting and power to the usb cam 

$fn=360;

//first test print of cross beam to fit in the arm and be screwed in place
crossBeam = [5,5,51];
screwD = 3 ;
wiggle = 0.01;
difference(){
    cube(crossBeam);
    translate([crossBeam.x/2, crossBeam.y/2, -wiggle/2]) cylinder(h = crossBeam.z + wiggle, d = screwD);
}