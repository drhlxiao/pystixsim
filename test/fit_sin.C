double fun(double *x, double *p){
	return  p[0]+p[1]*sin(p[2]*x[0]+p[3]);
}

void fit_sin()
{
//	double y[12]={1.36360105, 3.84579248, 3.78205783,  1.31729735, 1.35796924 ,3.84579014,
//		3.78205783,1.31654736,0.0105756, 0.21638967,0.34385665,0.09830119};
//	double y[12]={4.08114161, 1.99908683, 0.88988817, 2.95525983, 4.06705392, 1.99427544,
//		 0.90778025, 2.98661243, 0.3833843,  0.23089828, 0.05462554, 0.22189553};
	double y[12]={1.36360105, 3.84579248, 3.78205783, 1.31729735, 1.35796924 ,3.84579014, 3.78205783, 1.31654736, 0.0105756,  0.21638967 ,0.34385665, 0.09830119};
    //#fit_pattern(pat)
	double x[12]={0};
	double sum=0;
	double max=0;
	double min=100;
	double num=4;
	int off=4;
	for(int i=0;i<num;i++)
	{
		sum+=y[i+off];
		x[i]=i;
		if(y[i+off]>max)max=y[i+off];
		if(y[i+off]<min)min=y[i+off];
	}


	int n=(int)num;
	TGraph *gr=new TGraph(n, x,y);
	TF1 *f1=new TF1("fun",fun,0,n, 4);
	double base=sum/num;
	double amp=(max-min)/2;
	double freq=2*3.1415/4; //4 pixels


	 f1->SetParameters(0,base);
	 f1->SetParameters(1,amp);
	 f1->SetParameters(2,freq);
	 f1->SetParameters(3,0);
	 f1->SetParLimits(0,0.5*base, 1.5*base);
	 f1->SetParLimits(1,0.5* amp, 1.5*amp);
	 f1->SetParLimits(2,0.01*freq, 1.*freq);
	 f1->SetParLimits(3,0,2*3.1415);

	gr->Draw("ALP");
	gr->Fit(f1,"R");

}
