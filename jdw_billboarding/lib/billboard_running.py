# Purpose: Highest-level billboarding calls for the main usage scenarios (setup/configure/run/nrt).

from dataclasses import dataclass
from pythonosc.osc_bundle import OscBundle
from pythonosc.osc_message import OscMessage

from jdw_billboarding.lib.billboard_osc_conversion import NrtBundleInfo, get_all_command_messages, get_all_effects_create, get_all_effects_mod, get_nrt_record_bundles, get_sampler_keyboard_config, get_sequencer_batch_queue_bundle, get_synth_keyboard_config
from jdw_billboarding.lib.billboard_construction import parse_billboard

from jdw_billboarding.lib.billboard_classes import Billboard, CommandContext
from jdw_billboarding.lib.external_data_classes import SampleMessage, SynthDefMessage
from jdw_billboarding.lib.jdw_osc_utils import create_nrt_preload_bundle

from jdw_billboarding.lib.jdw_osc_utils import create_msg

# TODO: No hard link for the common prefix yet
def get_effects_clear() -> OscMessage:
    common_prefix = "effect_"
    return create_msg("/free_notes", ["^" + common_prefix + "(.*)"])

def get_configuration_messages(bbd_content: str) -> list[OscMessage]:
    billboard: Billboard = parse_billboard(bbd_content)

    all_messages: list[OscMessage] = []

    all_messages += get_sampler_keyboard_config(billboard)
    all_messages += get_synth_keyboard_config(billboard)

    all_messages += [get_effects_clear()]
    all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.UPDATE])
    all_messages += get_all_effects_create(billboard)

    return all_messages

@dataclass
class NrtData:
    main_bundle: OscBundle
    preload_messages: list[OscMessage]
    preload_bundle_batches: list[OscBundle]

# TODO: synthdefs and samples are vagrant, but it's hard to package neatly without...
def get_nrt_data(bbd_content: str, all_synthdefs: list[SynthDefMessage], all_samples: list[SampleMessage]) -> list[NrtData]:
    billboard: Billboard = parse_billboard(bbd_content)
    nrt_info: list[NrtBundleInfo] = get_nrt_record_bundles(billboard, all_synthdefs, all_samples)
    export: list[NrtData] = []
    for info in nrt_info:
        # Just some batching hack I stole off stackoverflow
        batch_size = 10
        preload_batches: list[list[OscBundle]] = [info.preload_bundles[i * batch_size:(i + 1) * batch_size] for i in range((len(info.preload_bundles) + batch_size - 1) // batch_size )]
        export.append(NrtData(info.nrt_bundle, info.preload_messages, [create_nrt_preload_bundle(batch) for batch in preload_batches]))

    return export

def get_queue_update_packets(bbd_content: str) -> list[OscBundle | OscMessage]:
    billboard: Billboard = parse_billboard(bbd_content)

    all_messages: list[OscMessage | OscBundle] = []

    # Keyboard is configured on regular run as well
    all_messages += get_synth_keyboard_config(billboard)
    all_messages += get_sampler_keyboard_config(billboard)
    all_messages += get_all_command_messages(billboard, [CommandContext.ALL, CommandContext.QUEUE])
    all_messages += get_all_effects_mod(billboard)
    all_messages += [get_sequencer_batch_queue_bundle(billboard)]

    return all_messages
