# RAG Generation with watsonx.data and Milvus

![WatsonX](wxd-images/watsonxlogoibm.png)

The next-gen watsonx.data lakehouse is designed to overcome the costs and complexities enterprises face. This will be the world’s first and only open data store with multi-engine support that is built for hybrid deployment across your entire ecosystem.
 
   * WatsonX.data is the only lakehouse with multiple query engines allowing you to optimize costs and performance by pairing the right workload with the right engine.
   * Run all workloads from a single pane of glass, eliminating trade-offs with convenience while still improving cost and performance.
   * Deploy anywhere with full support for hybrid-cloud and multi cloud environments.
   * Shared metadata across multiple engines eliminates the need to re-catalog, accelerating time to value while ensuring governance and eliminating costly implementation efforts.

This lab uses the watsonx.data developer package. The Developer package is meant to be used on single nodes. While it uses the same code base, there are some restrictions, especially on scale. In this lab, we will open some additional ports as well to understand how everything works. We will also use additional utilities to illustrate connectivity and what makes the watsonx.data system "open". 

We organized this lab into a number of sections that cover many of the highlights and key features of watsonx.data.

   * Access a TechZone or VMWare image for testing
   * Checking watsonx.data status
   * Introduction to watsonx.data components
   * Analytical SQL
   * Advanced SQL functions
   * Time Travel and Federation
   * Working with Object Store Buckets

In addition, there is an Appendix which includes common errors and potential fixes or workarounds. 

## Watsonx.data Developer Image 

The watsonx.data system is running on a virtual machine with the following resources:

   * 4 vCPUs
   * 16Gb of memory
   * 400Gb of disk

This is sufficient for running this exercises found in this lab but should not be used for performance testing or dealing with large data sets.

## Watsonx.data Level 3 Technical Training

This system is used as a basis for the watsonx.data Level 3 Technical Training. For the detailed lab material, please refer to the following PDF found in Seismic: [https://ibm.seismic.com/Link/Content/DCG37pjmPj7VmGCHj2Df8fHVmDJj](https://ibm.seismic.com/Link/Content/DCG37pjmPj7VmGCHj2Df8fHVmDJj)
