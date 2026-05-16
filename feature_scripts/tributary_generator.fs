FeatureScript 2559;

//--------------------------------------------------
// Imports recovered from the original Tributaryv1 work.
//--------------------------------------------------
import(path : "onshape/std/geometry.fs", version : "2559.0");
import(path : "onshape/std/sketch.fs", version : "2559.0");
import(path : "onshape/std/units.fs", version : "2559.0");
import(path : "onshape/std/string.fs", version : "2559.0");

// =============================================================================
// Tributary Generator
// =============================================================================
// Portfolio-facing Onshape FeatureScript candidate.
//
// This file is the CAD-side partner to the Python preview package in:
//     src/tributary_geometry/
//
// What it creates
// ---------------
// A sketch-level tributary/flow-field construction made from:
//   1. feed source circles on the left source line;
//   2. dump source circles on the middle source line;
//   3. alternating snake/ladder construction circles on the central target line;
//   4. top and bottom cubic Bezier channel boundaries between those circle sets.
//
// Why this file is heavily annotated
// ----------------------------------
// FeatureScript syntax and unit/type behavior were constant problems during the
// original work. That history is not hidden here. The code is intentionally
// explicit around Id use, unit-bearing distances, vector construction, Bezier
// point keys, and array indexing. See docs/150_SYNTAX_AND_DEBUGGING_HISTORY.md.
//
// Status
// ------
// The Python geometry mirror is locally validated and gives fast SVG/PNG/JSON
// previews. This FeatureScript is a cleaned Onshape candidate and still requires
// Onshape-side compile/regeneration validation.
// =============================================================================

// Treat an Onshape variable as an integer count.
function _tgAsCount(value)
{
    return floor(value + 0.5);
}

// Central-line y position, symmetric about the sketch midline y = 0.
// The recovered v1 document used 2 * Channel_Num_Snakes + 1 central stations,
// which gives a real center snake circle on the midline.
function _tgCenterY(index, centerCount, length)
{
    if (centerCount <= 1)
    {
        return 0 * meter;
    }
    return length / 2 - index * length / (centerCount - 1);
}

// Source feed-line interior y position.
function _tgFeedY(index, nSnakes, manifoldLength)
{
    return manifoldLength / 2 - manifoldLength * (index + 1) / nSnakes;
}

// Source dump-line half-step y position.
function _tgDumpY(index, nSnakes, manifoldLength)
{
    return manifoldLength / 2 - (manifoldLength / (2 * nSnakes) + manifoldLength * index / nSnakes);
}

// These helpers return the channel-boundary points on the facing envelope of a
// construction circle. They are not circle centers. They represent the upper and
// lower channel edges approaching/leaving a circular port envelope.
function _tgRightTop(c, r)
{
    return vector(c[0] + r, c[1] + r);
}

function _tgRightBottom(c, r)
{
    return vector(c[0] + r, c[1] - r);
}

function _tgLeftTop(c, r)
{
    return vector(c[0] - r, c[1] + r);
}

function _tgLeftBottom(c, r)
{
    return vector(c[0] - r, c[1] - r);
}

// Rectangular d_M1/d_M2 control construction.
//
// The old v1 document's diagram showed d_M1 and d_M2 as horizontal distances
// inside a construction rectangle, not as perpendicular offsets from a centerline.
// This helper therefore creates:
//   P0 = source boundary point
//   P1 = P0 shifted horizontally toward the target by d_M1
//   P2 = P3 shifted horizontally back toward the source by d_M2
//   P3 = target boundary point
function _tgBezierControlPointsRect(pB, pE, d_M1, d_M2)
{
    var xSign = 1;
    if (pE[0] < pB[0])
    {
        xSign = -1;
    }
    return [
        pB,
        vector(pB[0] + xSign * d_M1, pB[1]),
        vector(pE[0] - xSign * d_M2, pE[1]),
        pE
    ];
}

// Draw one cubic Bezier channel boundary and, optionally, its control handles.
// The Bezier key is "points" because that was the syntax used in the recovered
// v1 document. Earlier attempts using alternate keys were a recurring source of
// FeatureScript syntax/regen trouble.
function _tgDrawBezierBoundary(sketch is Sketch, idBase is string, pB, pE, d_M1, d_M2, showConstruction is boolean)
{
    var pts = _tgBezierControlPointsRect(pB, pE, d_M1, d_M2);

    if (showConstruction)
    {
        skLineSegment(sketch, idBase ~ "_handle_start", {
                    "start" : pts[0],
                    "end" : pts[1],
                    "construction" : true
                });
        skLineSegment(sketch, idBase ~ "_handle_end", {
                    "start" : pts[2],
                    "end" : pts[3],
                    "construction" : true
                });
        skPoint(sketch, idBase ~ "_P1", { "position" : pts[1], "construction" : true });
        skPoint(sketch, idBase ~ "_P2", { "position" : pts[2], "construction" : true });
    }

    skBezier(sketch, idBase, {
                "points" : pts,
                "construction" : false
            });
}

// Draw the rectangle that explains a top/bottom boundary pair.
function _tgDrawConstructionRectangle(sketch is Sketch, idBase is string, sourceTop, sourceBottom, targetTop, targetBottom)
{
    skLineSegment(sketch, idBase ~ "_rect_top", { "start" : sourceTop, "end" : targetTop, "construction" : true });
    skLineSegment(sketch, idBase ~ "_rect_right", { "start" : targetTop, "end" : targetBottom, "construction" : true });
    skLineSegment(sketch, idBase ~ "_rect_bottom", { "start" : targetBottom, "end" : sourceBottom, "construction" : true });
    skLineSegment(sketch, idBase ~ "_rect_left", { "start" : sourceBottom, "end" : sourceTop, "construction" : true });
}

// Draw both physical boundaries for one tributary channel.
function _tgDrawTributaryPair(sketch is Sketch, idBase is string, sourceCenter, sourceRadius, targetCenter, targetRadius, d_M1, d_M2, showConstruction is boolean)
{
    var sourceTop = _tgRightTop(sourceCenter, sourceRadius);
    var sourceBottom = _tgRightBottom(sourceCenter, sourceRadius);
    var targetTop = _tgLeftTop(targetCenter, targetRadius);
    var targetBottom = _tgLeftBottom(targetCenter, targetRadius);

    if (showConstruction)
    {
        _tgDrawConstructionRectangle(sketch, idBase, sourceTop, sourceBottom, targetTop, targetBottom);
    }

    _tgDrawBezierBoundary(sketch, idBase ~ "_top", sourceTop, targetTop, d_M1, d_M2, showConstruction);
    _tgDrawBezierBoundary(sketch, idBase ~ "_bottom", sourceBottom, targetBottom, d_M1, d_M2, showConstruction);
}

annotation { "Feature Type Name" : "Tributary Generator" }
export const tributaryGenerator = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Sketch plane", "Filter" : EntityType.FACE && GeometryType.PLANE, "MaxNumberOfPicks" : 1 }
        definition.sketchPlane is Query;

        annotation { "Name" : "Show construction helpers", "Default" : true }
        definition.showConstruction is boolean;
    }
    {
        // ---------------------------------------------------------------------
        // 1. Read external Onshape variables.
        // ---------------------------------------------------------------------
        var nSnakes = _tgAsCount(getVariable(context, "Channel_Num_Snakes"));
        if (nSnakes < 2)
        {
            throw regenError("Channel_Num_Snakes must be at least 2.");
        }

        var manifoldLength = getVariable(context, "Manifold_Length");
        var manifoldReduction = getVariable(context, "Manifold_Reduction");
        var ladderWidth = getVariable(context, "Ladder_Width");
        var feedDumpOffset = getVariable(context, "FeedDump_Offset");
        var tributaryOffset = getVariable(context, "Tributary_Offset");
        var feedDiameter = getVariable(context, "Feed_Diameter");
        var dumpDiameter = getVariable(context, "Dump_Diameter");
        var snakeWidth = getVariable(context, "Snake_Width");
        var dSnakeM1 = getVariable(context, "d_snake_M1");
        var dSnakeM2 = getVariable(context, "d_snake_M2");
        var dLadderM1 = getVariable(context, "d_ladder_M1");
        var dLadderM2 = getVariable(context, "d_ladder_M2");

        // ---------------------------------------------------------------------
        // 2. Derived counts, lengths, radii, and x locations.
        // ---------------------------------------------------------------------
        var feedCount = nSnakes - 1;
        var dumpCount = nSnakes;
        var centralCount = 2 * nSnakes + 1;

        // This is the old v1 central-line length expression.
        var centralLength = manifoldLength + 2 * manifoldReduction - 2 * ladderWidth;
        if (centralLength <= 0 * meter)
        {
            throw regenError("Central snake/ladder line length is not positive. Check Manifold_Length, Manifold_Reduction, and Ladder_Width.");
        }

        var feedRadius = feedDiameter / 2;
        var dumpRadius = dumpDiameter / 2;
        var snakeRadius = snakeWidth / 2;
        var ladderRadius = ladderWidth / 2;

        // Coordinate convention matches the Python preview:
        //   feed line   x = 0
        //   dump line   x = FeedDump_Offset
        //   target line x = FeedDump_Offset + Tributary_Offset
        var feedX = 0 * meter;
        var dumpX = feedDumpOffset;
        var centralX = feedDumpOffset + tributaryOffset;

        // ---------------------------------------------------------------------
        // 3. Create the sketch on the selected planar face.
        // ---------------------------------------------------------------------
        var facePlane = evPlane(context, { "face" : definition.sketchPlane });
        var sketchPlane = plane(facePlane.origin, facePlane.normal, facePlane.x);
        var sketch = newSketchOnPlane(context, id, { "sketchPlane" : sketchPlane });

        var snakeCenters = [];
        var ladderCenters = [];
        var feedCenters = [];
        var dumpCenters = [];

        // ---------------------------------------------------------------------
        // 4. Central alternating snake/ladder target line.
        // ---------------------------------------------------------------------
        // With N = Channel_Num_Snakes, this creates:
        //   snake centers:  N + 1, including the exact middle symmetry station
        //   ladder centers: N, between the snake centers
        for (var ci = 0; ci < centralCount; ci += 1)
        {
            var cy = _tgCenterY(ci, centralCount, centralLength);
            if (ci % 2 == 0)
            {
                var snakeIndex = floor(ci / 2);
                var snakeCenter = vector(centralX, cy);
                snakeCenters = append(snakeCenters, snakeCenter);
                skCircle(sketch, "snakeCircle_" ~ snakeIndex, {
                            "center" : snakeCenter,
                            "radius" : snakeRadius,
                            "construction" : true
                        });
            }
            else
            {
                var ladderIndex = floor(ci / 2);
                var ladderCenter = vector(centralX, cy);
                ladderCenters = append(ladderCenters, ladderCenter);
                skCircle(sketch, "ladderCircle_" ~ ladderIndex, {
                            "center" : ladderCenter,
                            "radius" : ladderRadius,
                            "construction" : true
                        });
            }
        }

        // Optional visual midline so the symmetry is visible in Onshape.
        if (definition.showConstruction)
        {
            skLineSegment(sketch, "symmetry_midline", {
                        "start" : vector(feedX - feedRadius, 0 * meter),
                        "end" : vector(centralX + snakeRadius, 0 * meter),
                        "construction" : true
                    });
        }

        // ---------------------------------------------------------------------
        // 5. Source feed and dump circle lines.
        // ---------------------------------------------------------------------
        // These source y positions are the old v1 formulas. The first/last feed
        // circles shift left by one feed radius, also recovered from prior notes.
        for (var fi = 0; fi < feedCount; fi += 1)
        {
            var feedShift = 0 * meter;
            if (fi == 0 || fi == feedCount - 1)
            {
                feedShift = -feedRadius;
            }
            var feedCenter = vector(feedX + feedShift, _tgFeedY(fi, nSnakes, manifoldLength));
            feedCenters = append(feedCenters, feedCenter);
            skCircle(sketch, "feedCircle_" ~ fi, {
                        "center" : feedCenter,
                        "radius" : feedRadius,
                        "construction" : true
                    });
        }

        for (var di = 0; di < dumpCount; di += 1)
        {
            var dumpCenter = vector(dumpX, _tgDumpY(di, nSnakes, manifoldLength));
            dumpCenters = append(dumpCenters, dumpCenter);
            skCircle(sketch, "dumpCircle_" ~ di, {
                        "center" : dumpCenter,
                        "radius" : dumpRadius,
                        "construction" : true
                    });
        }

        // ---------------------------------------------------------------------
        // 6. Build the tributaries.
        // ---------------------------------------------------------------------
        // The default CAD implementation follows the Python GUI default:
        //   feed circles -> interior snake circles
        //   dump circles -> ladder circles
        //
        // This respects the middle symmetry and gives the photo-like physical
        // tributary row. The literal old note that described feed->ladder and
        // dump->snake is preserved in the Python GUI as recovered_docx_v1.
        for (var i = 0; i < feedCount; i += 1)
        {
            _tgDrawTributaryPair(sketch, "feed_to_snake_" ~ i,
                feedCenters[i], feedRadius,
                snakeCenters[i + 1], snakeRadius,
                dLadderM1, dLadderM2,
                definition.showConstruction);
        }

        for (var j = 0; j < dumpCount; j += 1)
        {
            _tgDrawTributaryPair(sketch, "dump_to_ladder_" ~ j,
                dumpCenters[j], dumpRadius,
                ladderCenters[j], ladderRadius,
                dSnakeM1, dSnakeM2,
                definition.showConstruction);
        }

        skSolve(sketch);
    });
