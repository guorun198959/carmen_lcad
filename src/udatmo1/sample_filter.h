#ifndef SAMPLEFILTER_H_
#define SAMPLEFILTER_H_

/*

FIR filter designed with
 http://t-filter.appspot.com

sampling frequency: 20 Hz

* 0 Hz - 0.25 Hz
  gain = 1
  desired ripple = 0.5 dB
  actual ripple = 0.30817680462821617 dB

* 0.75 Hz - 10 Hz
  gain = 0
  desired attenuation = -40 dB
  actual attenuation = -41.6311546814326 dB

*/

#define SAMPLEFILTER_TAP_NUM 73

namespace udatmo
{

class SampleFilter
{
  double history[SAMPLEFILTER_TAP_NUM];

  unsigned int last_index;

public:
	SampleFilter();

	SampleFilter &operator += (double input);

	double operator () ();
};

} // namespace udatmo

#endif
