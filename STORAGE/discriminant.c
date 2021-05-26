/*@ axiomatic FP_ulp {
  @ logic real ulp(double f);
  @
  @ axiom ulp_normal1 :
  @   \forall double f; 0x1p-1022 <= \abs(f) 
  @       ==>\abs(f) < 0x1.p53 * ulp(f) ;
  @
  @ axiom ulp_normal2 :
  @   \forall double f; 0x1p-1022 <= \abs(f) 
  @       ==> ulp(f) <= 0x1.p-52 * \abs(f);
  @ axiom ulp_subnormal :
  @   \forall double f; \abs(f) <  0x1p-1022
  @       ==> ulp(f) == 0x1.p-1074;
  @ axiom ulp_pow :
  @   \forall double f; \exists integer i; 
  @         ulp(f) == \pow(2.,i);
  @ } */


/*@ ensures \result==\abs(f); */
double fabs(double f);


/*@ requires xy == \round_double(\NearestEven,x*y) && 
  @          \abs(x) <= 0x1.p995 && 
  @          \abs(y) <= 0x1.p995 &&
  @          \abs(x*y) <=  0x1.p1021;
  @ ensures  ((x*y == 0 || 0x1.p-969 <= \abs(x*y)) 
  @                 ==> x*y == xy+\result);
  @*/
double Dekker(double x, double y, double xy);



/* If no Underflow occur, the result is within 2 ulps 
   of the correct result */

/*@ requires 
  @     (b==0.   || 0x1.p-916 <= \abs(b*b)) &&
  @     (a*c==0. || 0x1.p-916 <= \abs(a*c)) &&
  @     \abs(b) <= 0x1.p510 && \abs(a) <= 0x1.p995 && \abs(c) <= 0x1.p995 && 
  @     \abs(a*c) <= 0x1.p1021;
  @ ensures \result==0.  || \abs(\result-(b*b-a*c)) <= 2.*ulp(\result);
  @ */


double discriminant(double a, double b, double c) {
  double p,q,d,dp,dq;
  p=b*b;
  q=a*c;
  
  if (p+q <= 3*fabs(p-q))
    d=p-q;
  else {
    dp=Dekker(b,b,p);
    dq=Dekker(a,c,q);
    d=(p-q)+(dp-dq);
  }
  return d;
}
