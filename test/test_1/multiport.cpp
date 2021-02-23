#include "multiport.h"
#include "configuredpins.h"

MultiPort mp = MultiPort(0, 1, 100, 2);
bool last_state = false;
uint16_t last_slot = 9999;

void setSlot(uint16_t slot, uint16_t state) {
    last_state = state;
    last_slot = slot;
    digitalWrite(last_slot, last_state);
}

void address_test() {
    TEST_ASSERT(mp.check_address(100));
    TEST_ASSERT(mp.check_address(106));
    TEST_ASSERT_FALSE(mp.check_address(107));
    TEST_ASSERT_FALSE(mp.check_address(99));
}

void output_test() {
    last_slot = 9999;
    last_state = false;
    mp.check_address(100);
    mp.set(1, 1); // Set bit 1
    TEST_ASSERT_FALSE(last_state);
    TEST_ASSERT_EQUAL(9999, last_slot);
    mp.check_address(106);
    mp.set(0, 1); // Set new position
    TEST_ASSERT(last_state);
    TEST_ASSERT_EQUAL(last_slot, 3);
    last_state = false;
    last_slot = 9999;
    mp.check_address(100);
    mp.set(1, 1); // Set bit 0
    mp.check_address(102);
    mp.set(1, 1); // Set bit 2
    mp.check_address(106);
    mp.set(0, 1); // Set new position
    TEST_ASSERT(last_state);
    TEST_ASSERT_EQUAL(last_slot, 7);
    TEST_ASSERT_EQUAL(5, mp.get_state());
    mp.restore_state(2);
    TEST_ASSERT(mp.update());
    _delay_ms(210);
    TEST_ASSERT_FALSE(mp.update());
    TEST_ASSERT_FALSE(last_state);
    TEST_ASSERT_EQUAL(last_slot, 4);
}

void update_test() {
    last_state = false;
    last_slot = 9999;
    TEST_ASSERT_FALSE(mp.update())
    mp.check_address(100);
    mp.set(1, 1); // Set bit 0
    mp.check_address(103);
    mp.set(1, 1); // Set bit 3
    mp.check_address(106);
    mp.set(0, 1); // Set new position
    TEST_ASSERT(last_state);
    TEST_ASSERT_EQUAL(last_slot, 11);
    TEST_ASSERT(mp.update());
    _delay_ms(210);
    TEST_ASSERT_FALSE(mp.update());
    TEST_ASSERT_FALSE(last_state);
    TEST_ASSERT_EQUAL(last_slot, 11);

}
void setup(){
    UNITY_BEGIN();
    pinMode(11, OUTPUT);
    RUN_TEST(update_test);
    RUN_TEST(address_test);
    RUN_TEST(output_test);
}

void loop(){
    UNITY_END();
}