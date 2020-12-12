from pygmyhdl import *

@chunk
def pwm_simple(clk_i, pwm_o, threshold):

    cnt = Bus(len(threshold), name='cnt')

    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1

    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold


initialize()


clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(3, init_val=3)
pwm_simple(clk, pwm, threshold)

clk_sim(clk, num_cycles=24)
show_text_table()
show_waveforms(start_time=13, tock=True)



def test_bench(num_cycles):
    clk.next = 0
    threshold.next = 3
    yield delay(1)
    for cycle in range(num_cycles):
        clk.next = 0

        if cycle >= 14:
            threshold.next = 8
        yield delay(1)
        clk.next = 1
        yield delay(1)


simulate(test_bench(20))
show_waveforms(tick=True, start_time=19)
show_text_table()


@chunk
def ramp(clk_i, ramp_o):

    delta = Bus(len(ramp_o))

    @seq_logic(clk_i.posedge)
    def logic():

        ramp_o.next = ramp_o + delta
        if ramp_o == 1:
            delta.next = 1
        elif ramp_o == ramp_o.max - 2:
            delta.next = -1
        elif delta == 0:
            delta.next = 1
            ramp_o.next = 1

@chunk
def wax_wane(clk_i, led_o, length):
    rampout = Bus(length, name='ramp')
    ramp(clk_i, rampout)
    pwm_simple(clk_i, led_o, rampout.o[length:length-4])


initialize()
clk = Wire(name='clk')
led = Wire(name='led')
wax_wane(clk, led, 6)

clk_sim(clk, num_cycles=180)
t = 110
show_text_table(start_time=t, stop_time=t+40)

toVerilog(wax_wane, clk, led, 23)
