# Copyright 2010 John Carr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Provides simple close-range navigation, based on
#   golem (http://github.com/aniero/golem)

import heapq

MAX_PATH_SIZE = 64


class Heap(object):

    __slots__ = ("sortfn", "heap", )

    def __init__(self, sortfn=lambda x: x):
        self.sortfn = sortfn
        self.heap = []
        heapq.heapify(self.heap)

    def push(self, x):
        heapq.heappush(self.heap, (self.sortfn(x), x))

    def pop(self):
        sortval, val = heapq.heappop(self.heap)
        return val

    def empty(self):
        return len(self.heap) == 0


class Path(object):

    __slots__ = ("point", "goals", "path")

    def __init__(self, point, goals, path):
        self.point = point
        self.goals = goals
        self.path = path

    def cost(self):
        """
        I return a value to help sort paths by their efficiency
        """
        heuristic = min((goal-self.point).manhattan_length() for goal in self.goals)
        # scale heuristic by 1% for better efficiency
        # favors expansion near goal over expansion from start
        # via http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#S12
        return heuristic * 101 + len(self.path) * 100


def path(world, start, goals):
    start = start.floor()

    # Make sure there is a goal in range
    if not filter(lambda x: x.manhattan_length() <= MAX_PATH_SIZE, goals):
        return None

    # Check the goal is actually valid...
    if not filter(lambda x: world.allowed(x), goals):
        return None

    visited = set()
    examined = 0

    heap = Heap(lambda x: x.cost())
    heap.push(Path(start, goals, []))

    while not heap.empty():
        path = heap.pop()

        if path.point in visited:
            continue
        visited.add(path.point)

        examined += 1

        if path.point in goals:
            final_path = path.path + [path.point]
            final_path = final_path[1:]
            return final_path

        for next_point in world.available(path.point):
            if next_point in visited:
                continue
            heap.push(Path(next_point, goals, path.path + [path.point]))

