res1 = 0.01;
res2 = 0.005;

res_boundary = 0.015;
res_circle = 0.015;
res_flag = 0.015;

// Tube domain
Point(1) = {0, 0, 0, res_boundary};
Point(2) = {0, 0.41, 0, res_boundary};
Point(3) = {2.5, 0.41, 0, res_boundary};
Point(4) = {2.5, 0, 0, res_boundary};

// Circle
Point(5) = {0.2, 0.2, 0, res_circle};
Point(7) = {0.2, 0.15, 0, res_circle};
Point(8) = {0.2, 0.25, 0, res_circle};
Point(9) = {0.15, 0.2, 0, res_circle};
Point(10) = {0.2489897949, 0.21, 0.0, res_circle};
Point(11) = {0.2489897949, 0.19, 0.0, res_circle};

//Flag end points
Point(12) = {0.6, 0.19, 0, res_flag};
Point(13) = {0.6, 0.21, 0, res_flag};

//Extra point Flag
Point(22) = {0.32, 0.21, 0.0, res_flag};
Point(23) = {0.32, 0.19, 0.0, res_flag};

Point(14) = {0.43, 0.19, 0, res_flag};
Point(15) = {0.43, 0.21, 0, res_flag};

//Extra points boundary
Point(16) = {0.43, 0.0, 0, res_boundary};
Point(17) = {0.43, 0.41, 0, res_boundary};

Point(18) = {1.5, 0.0, 0, res_boundary};
Point(19) = {1.5, 0.41, 0, res_boundary};

Point(20) = {0.9, 0.0, 0, res_boundary};
Point(21) = {0.9, 0.41, 0, res_boundary};



Circle(18) = {9, 5, 8};
Circle(19) = {8, 5, 10};
Circle(20) = {10, 5, 11};
Circle(21) = {11, 5, 7};
Circle(22) = {7, 5, 9};




// Field[1] = BoundaryLayer;
// Field[1].EdgesList = {18,19,21,22,33};
// Field[1].hwall_n = 0.001;
// Field[1].ratio = 1.5;
// Field[1].thickness = 0.005;
// Field[1].Quads = 0;
// BoundaryLayer Field = 1;
/*
Transfinite Line{20,-25,-24,-23} = 6;
Transfinite Surface{103};
*/
//+
Line(23) = {2, 17};
//+
Line(24) = {17, 21};
//+
Line(25) = {21, 19};
//+
Line(26) = {19, 3};
//+
Line(27) = {3, 4};
//+
Line(28) = {4, 18};
//+
Line(29) = {18, 20};
//+
Line(30) = {20, 16};
//+
Line(31) = {16, 1};
//+
Line(32) = {1, 2};
//+
Line(33) = {10, 22};
//+
Line(34) = {22, 15};
//+
Line(35) = {15, 13};
//+
Line(36) = {13, 12};
//+
Line(37) = {12, 14};
//+
Line(38) = {14, 23};
//+
Line(39) = {23, 11};
//+
Line Loop(1) = {23, 24, 25, 26, 27, 28, 29, 30, 31, 32};
//+
Line Loop(2) = {19, 33, 34, 35, 36, 37, 38, 39, 21, 22, 18};
//+
Plane Surface(1) = {1, 2};
//+
Line Loop(3) = {20, -39, -38, -37, -36, -35, -34, -33};
//+
Plane Surface(2) = {3};
