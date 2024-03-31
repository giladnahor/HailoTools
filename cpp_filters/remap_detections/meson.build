################################################
# Remap detections
################################################
remap_detections_sources = [
    'remap_detections.cpp'
]

shared_library('remap_detections_post',
    remap_detections_sources,
    dependencies : postprocess_dep,
    gnu_symbol_visibility : 'default',
    install: true,
    install_dir: meson.project_source_root() + '/resources/',
)
