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

from twisted.python import log


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
        #log.msg(point, goals, path)
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


def path(world, start, goals, mode="move"):
    start = start.floor()
    goals = [x.floor() for x in goals]

    # Make sure there is a goal in range
    if not filter(lambda x: (x-start).manhattan_length() <= MAX_PATH_SIZE, goals):
        log.msg("Goal is too far away")
        return None

    # Check the goal is actually valid...
    if not filter(lambda x: world.allowed(x), goals):
        log.msg("Goal isnt valid")
        return None

    visited = set()
    examined = 0

    heap = Heap(lambda x: x.cost())
    heap.push(Path(start, goals, []))

    while not heap.empty():
        path = heap.pop()

        if path.point in visited:
            #log.msg("rejecting ", path.point)
            continue
        visited.add(path.point)

        examined += 1
        #log.msg(examined, len(heap.heap))

        if path.point in goals:
            final_path = path.path + [path.point]
            final_path = final_path[1:]
            log.msg("FINAL PATH: ",  final_path)
            return final_path

        for next_points in world.available(path.point):
            if filter(lambda x: x in visited, next_points):
                continue
            #log.msg(next_point)
            heap.push(Path(next_points[:-1], goals, path.path + [path.point] + next_points[:-1]))

    #log.msg("Ran out of heap")

