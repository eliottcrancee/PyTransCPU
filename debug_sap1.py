from pytranscpu.cpu_sap1 import SAP1

cpu = SAP1()
print("Initial sequencer state:", cpu.sequencer.state)
cpu.load_program([0x00, 0xF0])
print("RAM 0:", cpu.ram.registers[0].state)
print("RAM 1:", cpu.ram.registers[1].state)

for step in range(15):
    print(f"--- STEP {step} ---")
    print(
        f"Seq: {cpu.sequencer.state}, PC: {cpu.program_counter.state[:4]}, IR: {cpu.instruction_register.state}, MAR: {cpu.memory_address.state[:4]}, ACC: {cpu.accumulator.state}, Halted: {cpu.halted}"
    )
    cpu.micro_step()
    if cpu.halted:
        print("Halted at step", step)
        break
