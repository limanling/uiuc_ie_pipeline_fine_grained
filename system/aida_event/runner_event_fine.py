from .fine_grained import fine_grained_events
from .framenet import new_event_framenet, new_event_dependency
import argparse

def event_fine_runner():
    fine_grained_events.runner(lang, ltf_source, edl_json_fine, edl_tab_freebase, edl_cs_coarse,
           filler_coarse, event_coarse_with_time, trans_file, event_fine, visualpath_fine, entity_finegrain_aida
           )
    print('event fine-grained typing done')
    new_event_framenet.extract_rel_framenet(framenet_path, ltf_source, rsd_source, edl_cs_coarse, filler_coarse, event_fine, event_frame)
    print("event extraction based on FrameNet done. ")
    new_event_dependency.extract_rel_dependency(rsd_source, corenlp_dir, edl_path, filler_path, event_path,
                           event_path_aug, new_event_path, visual_path)

    print("event extraction based on Dependency rules done. ")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('lang', type=str,
                        help='lang.')
    parser.add_argument('ltf_source', type=str,
                        help='ltf_source')
    parser.add_argument('edl_json_fine', default=str,
                        help='edl_json_fine')
    parser.add_argument('edl_tab_freebase', type=str,
                        help='edl_tab_freebase')
    parser.add_argument('edl_cs_coarse', default=str,
                        help='edl_cs_coarse')
    parser.add_argument('event_coarse_with_time', default=str,
                        help='event_coarse_with_time')
    parser.add_argument('event_fine', default=str,
                        help='event_fine')
    parser.add_argument('--visualpath_fine', default=None,
                        help='visualpath_fine')
    parser.add_argument('--trans_file', type=None,
                        help='trans_file')
    parser.add_argument('--filler_coarse', type=None,
                        help='filler_coarse')
    parser.add_argument('--entity_finegrain_aida', type=None,
                        help='entity_finegrain_aida')

    parser.add_argument('rsd_dir', type=str, help='rsd_dir')

    args = parser.parse_args()

    # ${lang} ${ltf_source} ${edl_json_fine} ${edl_tab_freebase} \
    #     #    ${edl_cs_coarse} ${event_coarse_with_time} ${event_fine} \
    # #    --filler_coarse ${filler_coarse} \
    # #    --edl_json_fine_aida ${edl_cs_fine_all}
    lang = args.lang
    ltf_source = args.ltf_source
    edl_json_fine = args.edl_json_fine
    edl_tab_freebase = args.edl_tab_freebase
    edl_cs_coarse = args.edl_cs_coarse
    filler_coarse = args.filler_coarse
    event_coarse_with_time = args.event_coarse_with_time
    trans_file = args.trans_file
    event_fine = args.event_fine
    visualpath_fine = args.visualpath_fine
    entity_finegrain_aida = args.entity_finegrain_aida

    # ${framenet_path} ${ltf_source} ${rsd_source} \
    #    ${edl_cs_coarse} ${filler_coarse} ${event_fine} ${event_frame}
    parser.add_argument('framenet_path', type=str, help='framenet_path')
    # parser.add_argument('ltf_source', type=str, help='ltf_source')
    parser.add_argument('rsd_source', type=str, help='rsd_source')
    # parser.add_argument('edl_cs_coarse', type=str, help='edl_cs_coarse')
    # parser.add_argument('filler_coarse', type=str, help='filler_coarse')
    # parser.add_argument('event_fine', type=str, help='event_fine')
    parser.add_argument('event_frame', type=str, help='event_frame')
    parser.add_argument('--visual_path_frame', type=str, help='visual_path_frame')

    framenet_path = args.framenet_path
    # ltf_source = args.ltf_source
    rsd_source = args.rsd_source
    # edl_cs_coarse = args.edl_cs_coarse
    # filler_coarse = args.filler_coarse
    # event_fine = args.event_fine
    event_frame = args.event_frame
    visual_path_frame = args.visual_path_frame

    # ${rsd_source} ${core_nlp_output_path} \
    #    ${edl_cs_coarse} ${filler_coarse} ${event_fine} ${event_frame} ${event_depen}
    parser.add_argument('rsd_source', type=str, help='rsd_source')
    parser.add_argument('core_nlp_output_path', type=str, help='core_nlp_output_path')
    parser.add_argument('edl_cs_coarse', type=str, help='edl_cs_coarse')
    parser.add_argument('filler_coarse', type=str, help='filler_coarse')
    parser.add_argument('event_path', type=str, help='event_path')
    parser.add_argument('event_path_aug', type=str, help='event_path_aug')
    parser.add_argument('new_event_path', type=str, help='new_event_path')
    parser.add_argument('--visual_path_dpen', type=str, help='visual_path_dpen')

    # args = parser.parse_args()
    # rsd_source = args.rsd_source
    corenlp_dir = args.corenlp_dir
    edl_path = args.edl_path
    filler_path = args.filler_path
    event_path = args.event_path
    event_path_aug = args.event_path_aug
    new_event_path = args.new_event_path
    visual_path_dpen =args.visual_path_dpen

    new_event_dependency.extract_rel_dependency(rsd_source, corenlp_dir, edl_path, filler_path, event_path,
                                                event_path_aug, new_event_path, visual_path_dpen)





