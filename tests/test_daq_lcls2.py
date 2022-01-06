import logging
from functools import partial
from threading import Event

import pytest
from ophyd.positioner import SoftPositioner
from ophyd.signal import Signal
from ophyd.utils.errors import WaitTimeoutError
from psdaq.control.ControlDef import ControlDef

from pcdsdaq.daq import DaqLCLS2

logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def daq_lcls2(RE) -> DaqLCLS2:
    return DaqLCLS2(
        platform=0,
        host='tst',
        timeout=1000,
        RE=RE,
        hutch_name='tst',
        sim=True,
    )


def test_state(daq_lcls2: DaqLCLS2):
    """Check that the state attribute reflects the DAQ state."""
    logger.debug('test_state')
    for state in ControlDef.states:
        if daq_lcls2.state_sig.get().name != state:
            state_change = daq_lcls2.get_status_for(check_now=False)
            daq_lcls2._control.sim_set_states(1, state)
            try:
                state_change.wait(timeout=1)
            except WaitTimeoutError:
                pass
        assert daq_lcls2.state == state


def test_preconfig(daq_lcls2: DaqLCLS2):
    """
    Check that preconfig has the following behavior:
    - Writes to cfg signals
    - Checks types, raising TypeError if needed
    - Has no change for unpassed kwargs
    - Reverts "None" kwargs to the default
    """
    logger.debug('test_preconfig')

    def test_one(keyword, good_values, bad_values):
        if keyword == 'motors':
            # Backcompat alias
            sig = daq_lcls2.controls_cfg
        else:
            sig = getattr(daq_lcls2, keyword + '_cfg')
        orig = sig.get()
        for value in good_values:
            daq_lcls2.preconfig(**{keyword: value})
            assert sig.get() == value
        some_value = sig.get()
        daq_lcls2.preconfig(show_queued_config=False)
        assert sig.get() == some_value
        for value in bad_values:
            with pytest.raises(TypeError):
                daq_lcls2.preconfig(**{keyword: value})
        daq_lcls2.preconfig(**{keyword: None})
        assert sig.get() == orig

    test_one('events', (1, 10, 100), (45.3, 'peanuts', object()))
    test_one('duration', (1, 2.3, 100), ('walnuts', object()))
    test_one('record', (True, False), (1, 0, object()))

    good_controls = dict(
        sig=Signal(name='sig'),
        mot=SoftPositioner(name='mot'),
    )
    for kw in ('controls', 'motors'):
        test_one(
            kw,
            (good_controls, list(good_controls.values())),
            ('text', 0, Signal(name='sig')),
        )
        # NOTE: we don't check that the contents of the controls are OK
        # This is a bit obnoxious to do generically

    test_one('begin_timeout', (1, 2.3, 100), ('cashews', object()))
    test_one('begin_sleep', (1, 2.3, 100), ('pistachios', object()))
    test_one('group_mask', (1, 10, 100), (23.4, 'coconuts', object()))
    test_one('detname', ('epix', 'wave8'), (1, 2.3, object()))
    test_one('scantype', ('cool', 'data'), (1, 2.4, object()))
    test_one('serial_number', ('213', 'AV34'), (1, 2.5, object()))
    test_one('alg_name', ('math', 'calc'), (1, 2.6, object()))
    test_one('alg_version', ([1, 2, 3], [2, 3, 4]), (1, 2.6, 'n', object()))


def test_record(daq_lcls2: DaqLCLS2):
    """
    Tests on record, record_cfg, recording_sig:

    Check that the recording_sig gets the correct value as reported by
    the monitorStatus calls.

    Then, check that the record property has the following behavior:
    - When setattr, record_cfg is put to as appropriate (True/False/None)
    - When getattr, we see the correct value:
      - True if the last set was True
      - False if the last set was False
      - Match the control's record state otherwise
    """
    ev = Event()

    def wait_for(goal, value, **kwargs):
        if value == goal:
            ev.set()

    # Establish that recording_sig is a reliable proxy for _control state
    for record in (True, False, True, False):
        ev.clear()
        daq_lcls2._control.setRecord(record)
        cbid = daq_lcls2.recording_sig.subscribe(partial(wait_for, record))
        ev.wait(1.0)
        daq_lcls2.recording_sig.unsubscribe(cbid)
        assert daq_lcls2.recording_sig.get() == record

    # Establish that record setattr works
    for record in (True, False, True, False):
        daq_lcls2.record = record
        assert daq_lcls2.record_cfg.get() == record

    # Establish that the getattr logic table is correct
    daq_cfg = (True, False, None)
    daq_status = (True, False)

    def assert_expected(daq: DaqLCLS2):
        if daq.record_cfg.get() is None:
            assert daq.record == daq.recording_sig.get()
        else:
            assert daq.record == daq.record_cfg.get()

    for cfg in daq_cfg:
        daq_lcls2.record_cfg.put(cfg)
        for status in daq_status:
            daq_lcls2.recording_sig.put(status)
            assert_expected(daq_lcls2)


@pytest.mark.skip(reason='Test not written yet.')
def test_run_number():
    # Should work at any point
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_stage_unstage():
    # Should work at any point
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_configure():
    # Test this after preconfig
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_config_info():
    # Test this after preconfig
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_default_config():
    # Test this after configure
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_configured():
    # Test this after configure
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_config():
    # Test this after configure
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_kickoff():
    # Test this after configure
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_wait():
    # Test this after kickoff
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_trigger():
    # Test this after kickoff
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_begin():
    # Test this after wait
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_stop():
    # Test this after begin
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_begin_infinite():
    # Test this after stop
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_end_run():
    # Test this after stop
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_read():
    # Test this after begin_infinite
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_pause_resume():
    # Test after begin_infinite
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_collect():
    # Test this after kickoff
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_complete():
    # Test this after collect
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_describe_collect():
    # Test this after collect
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_step_scan():
    # Test at the end
    1/0


@pytest.mark.skip(reason='Test not written yet.')
def test_fly_scan():
    # Test at the end
    1/0
