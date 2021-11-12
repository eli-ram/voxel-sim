#version 430

// {t} should be sorted in range (0 to 1)
layout (location = 0) in float t;

out float offset;

void main() {
    offset = t;
}