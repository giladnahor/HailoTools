/**
* Copyright (c) 2021-2022 Hailo Technologies Ltd. All rights reserved.
* Distributed under the LGPL license (https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt)
**/
#ifndef _HAILO_REMAP_DETECTIONS_HPP_
#define _HAILO_REMAP_DETECTIONS_HPP_
#include "hailo_objects.hpp"
#include "hailo_common.hpp"

__BEGIN_DECLS
void init(std::string config_path, std::string func_name);
void filter(HailoROIPtr roi);
__END_DECLS
#endif