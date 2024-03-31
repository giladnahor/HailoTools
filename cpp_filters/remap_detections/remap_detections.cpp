
/**
* Copyright (c) 2021-2022 Hailo Technologies Ltd. All rights reserved.
* Distributed under the LGPL license (https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt)

**/

#include <cmath>
#include <iostream>
#include <stdio.h>
#include <string>
#include <vector>
#include <time.h>
#include <map>
#include <memory>
#include <mutex>

// Tappas includes
#include "hailo_objects.hpp"
#include "hailo_common.hpp"
#include "remap_detections.hpp"

// void init(const std::string config_path, const std::string function_name){
//     try {
//       // Convert the string to an integer
//       keep_id = std::stoi(config_path);
//     } catch (const std::invalid_argument& e) {
//       std::cerr << "Error converting keep_id to int: " << e.what() << std::endl;
//     }
// }

void filter(HailoROIPtr roi)
{
  auto detections = hailo_common::get_hailo_detections(roi);
  std::vector<HailoObjectPtr> removed_detections;
  for (auto detection : detections ){
      // declare a vector of labels to keep
      std::vector<std::string> labels_to_keep = {"car", "truck", "bus"};
      //if (detection->get_label() is in the list of labels to keep)
      if (std::find(labels_to_keep.begin(), labels_to_keep.end(), detection->get_label()) != labels_to_keep.end()) {
          detection->set_class_id(1);
          detection->set_label("car");
      }
      else {
          removed_detections.push_back(detection);
      }
      hailo_common::remove_objects(roi, removed_detections);
  }
}