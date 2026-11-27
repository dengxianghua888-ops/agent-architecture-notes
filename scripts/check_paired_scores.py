"""Check the Crayotter–ChatCut comparison from arXiv:2606.07636v2, Appendix B, Table 3.

Source: https://arxiv.org/html/2606.07636v2#A2
Run with Python 3.8 or later. No third-party packages or network access required.
"""

from random import Random
from statistics import mean, quantiles


# Rows 001–023, in publication order. Each integer is the difference between
# the sums of the three human reviewers' scores, in tenths of a rating point.
# Row 001, for example: (24 + 32 + 28) - (18 + 26 + 18) = 22.
DIFFERENCES_IN_TENTHS = (
    22, 30, 66, 8, 6, 18, 56, 38, 4, 18, 8, -24,
    -36, -40, -48, -8, 16, 6, -24, 4, -8, 0, 4,
)
REVIEWERS = 3
RESAMPLES = 20_000
SEED = 20261127


def main():
    topics = len(DIFFERENCES_IN_TENTHS)
    topic_differences = [value / (10 * REVIEWERS) for value in DIFFERENCES_IN_TENTHS]
    gains = sum(value > 0 for value in topic_differences)
    ties = sum(value == 0 for value in topic_differences)
    losses = topics - gains - ties

    # Resample whole topics, preserving the original system/reviewer pairing.
    rng = Random(SEED)
    bootstrap = [
        mean(rng.choices(topic_differences, k=topics)) for _ in range(RESAMPLES)
    ]
    cuts = quantiles(bootstrap, n=40, method="inclusive")
    print(f"Topics higher / tied / lower for Crayotter: {gains} / {ties} / {losses}")
    print(f"Mean paired difference (1–5 scale): {mean(topic_differences):+.4f}")
    print(f"95% topic-bootstrap percentile interval: [{cuts[0]:+.4f}, {cuts[-1]:+.4f}]")


if __name__ == "__main__":
    main()
