from pygmyhdl import *
from math import ceil, log2


@chunk
def debouncer(clk_i, button_i, button_o, debounce_time):

    debounce_cnt = Bus(int(ceil(log2(debounce_time + 1))), name='dbcnt')
    prev_button = Wire(name='prev_button')

    @seq_logic(clk_i.posedge)
    def next_state_logic():
        if button_i == prev_button:
            if debounce_cnt != 0:
                debounce_cnt.next = debounce_cnt - 1
        else:
            debounce_cnt.next = debounce_time
        prev_button.next = button_i

    @seq_logic(clk_i.posedge)
    def output_logic():
        if debounce_cnt == 0:
            button_o.next = prev_button


@chunk
def classic_fsm(clk_i, inputs_i, outputs_o):

    fsm_state = State('A', 'B', 'C', 'D', name='state')
    reset_cnt = Bus(2)

    prev_inputs = Bus(len(inputs_i), name='prev_inputs')
    input_chgs = Bus(len(inputs_i), name='input_chgs')

    @comb_logic
    def detect_chg():
        input_chgs.next = inputs_i & ~prev_inputs

    @seq_logic(clk_i.posedge)
    def next_state_logic():
        if reset_cnt < reset_cnt.max - 1:
            reset_cnt.next = reset_cnt + 1
            fsm_state.next = fsm_state.s.A
        elif fsm_state == fsm_state.s.A:
            if input_chgs[0]:
                fsm_state.next = fsm_state.s.B
            elif input_chgs[1]:
                fsm_state.next = fsm_state.s.D
        elif fsm_state == fsm_state.s.B:
            if input_chgs[0]:
                fsm_state.next = fsm_state.s.C
            elif input_chgs[1]:
                fsm_state.next = fsm_state.s.A
        elif fsm_state == fsm_state.s.C:
            if input_chgs[0]:
                fsm_state.next = fsm_state.s.D
            elif input_chgs[1]:
                fsm_state.next = fsm_state.s.B
        elif fsm_state == fsm_state.s.D:
            if input_chgs[0]:
                fsm_state.next = fsm_state.s.A
            elif input_chgs[1]:
                fsm_state.next = fsm_state.s.C
        else:
            fsm_state.next = fsm_state.s.A

        prev_inputs.next = inputs_i

    @comb_logic
    def output_logic():
        if fsm_state == fsm_state.s.A:
            outputs_o.next = 0b0001
        elif fsm_state == fsm_state.s.B:
            outputs_o.next = 0b0010
        elif fsm_state == fsm_state.s.C:
            outputs_o.next = 0b0100
        elif fsm_state == fsm_state.s.D:
            outputs_o.next = 0b1000
        else:
            outputs_o.next = 0b1111


initialize()
inputs = Bus(2, name='inputs')
outputs = Bus(4, name='outputs')
clk = Wire(name='clk')
classic_fsm(clk, inputs, outputs)


def fsm_tb():

    nop = 0b00
    fwd = 0b01
    bck = 0b10

    ins = [nop, nop, nop, nop, fwd, fwd, fwd, bck, bck, bck]
    for inputs.next in ins:
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

    ins = [fwd, nop, fwd, nop, fwd, nop, bck, nop, bck, nop, bck, nop]
    for inputs.next in ins:
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)


simulate(fsm_tb())
show_text_table()
toVerilog(classic_fsm, clk_i=Wire(), inputs_i=Bus(2), outputs_o=Bus(4))
