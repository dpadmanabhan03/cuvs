# Copyright (c) 2024, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

header = """/*
 * Copyright (c) 2024, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * NOTE: this file is generated by generate_ivf_pq.py
 *
 * Make changes there and run in this directory:
 *
 * > python generate_ivf_pq.py
 *
 */

#include <cuvs/neighbors/ivf_pq.hpp>
"""

build_include_macro = """
#include "ivf_pq_build_extend_inst.cuh"
"""
search_include_macro = """
#include "../ivf_pq_search.cuh"
"""

namespace_macro = """
namespace cuvs::neighbors::ivf_pq {
"""

footer = """
}  // namespace cuvs::neighbors::ivf_pq
"""

types = dict(
    float_int64_t=("float", "int64_t"),
    half_int64_t=("half", "int64_t"),
    int8_t_int64_t=("int8_t", "int64_t"),
    uint8_t_int64_t=("uint8_t", "int64_t"),
)

build_extend_macro = ""  # moved to header ivf_pq_build_extend_inst.cuh

search_macro = """
#define CUVS_INST_IVF_PQ_SEARCH(T, IdxT)                                        \\
  void search(raft::resources const& handle,                                    \\
              const cuvs::neighbors::ivf_pq::search_params& params,             \\
              cuvs::neighbors::ivf_pq::index<IdxT>& index,                      \\
              raft::device_matrix_view<const T, IdxT, raft::row_major> queries, \\
              raft::device_matrix_view<IdxT, IdxT, raft::row_major> neighbors,  \\
              raft::device_matrix_view<float, IdxT, raft::row_major> distances, \\
              const cuvs::neighbors::filtering::base_filter& sample_filter_ref) \\
  {                                                                             \\
    cuvs::neighbors::ivf_pq::detail::search(                                    \\
      handle, params, index, queries, neighbors, distances, sample_filter_ref); \\
  }
"""

macros = dict(
    build_extend=dict(
        include=build_include_macro,
        definition=build_extend_macro,
        name="CUVS_INST_IVF_PQ_BUILD_EXTEND",
    ),
    search=dict(
        include=search_include_macro,
        definition=search_macro,
        name="CUVS_INST_IVF_PQ_SEARCH",
    ),
)

for type_path, (T, IdxT) in types.items():
    for macro_path, macro in macros.items():
        path = f"ivf_pq_{macro_path}_{type_path}.cu"
        with open(path, "w") as f:
            f.write(header)
            f.write(macro['include'])
            f.write(namespace_macro)
            f.write(macro["definition"])
            f.write(f"{macro['name']}({T}, {IdxT});\n\n")
            f.write(f"#undef {macro['name']}\n")
            f.write(footer)

        print(f"src/neighbors/ivf_pq/{path}")
