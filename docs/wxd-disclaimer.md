# Disclaimer
 
## Watson.data

Copyright © 2024 by International Business Machines Corporation (IBM). All
rights reserved. Printed in Canada. Except as permitted under the Copyright Act
of 1976, no part of this publication may be reproduced or distributed in any
form or by any means, or stored in a database or retrieval system, without the
prior written permission of IBM, with the exception that the program listings
may be entered, stored, and executed in a computer system, but they may not be
reproduced for publication.

The contents of this lab represent those features that may or may not be
available in the current release of any products mentioned within this lab
despite what the lab may say. IBM reserves the right to include or exclude any
functionality mentioned in this lab for the current release of watsonx.data, or
a subsequent release. In addition, any claims made in this lab are not official
communications by IBM; rather, they are observed by the authors in unaudited
testing and research. The views expressed in this lab is those of the authors
and not necessarily those of the IBM Corporation; both are not liable for any of
the claims, assertions, or contents in this lab.

IBM's statements regarding its plans, directions, and intent are subject to
change or withdrawal without notice and at IBM's sole discretion. Information
regarding potential future products is intended to outline our general product
direction and it should not be relied on in making a purchasing decision. The
information mentioned regarding potential future products is not a commitment,
promise, or legal obligation to deliver any material, code, or functionality.
Information about potential future products may not be incorporated into any
contract.

The development, release, and timing of any future feature or functionality
described for our products remains at our sole discretion.

Performance is based on measurements and projections using standard IBM
benchmarks in a controlled environment. The actual throughput or performance
that any user will experience will vary depending upon many factors, including
considerations such as the amount of multiprogramming in the user's job stream,
the I/O configuration, the storage configuration, and the workload processed.
Therefore, no assurance can be given that an individual user will achieve
results like those stated here.

U.S. Government Users Restricted Rights - Use, duplication or disclosure
restricted by GSA ADP Schedule Contract with IBM. Information in this eBook
(including information relating to products that have not yet been announced by
IBM) has been reviewed for accuracy as of the date of initial publication and
could include unintentional technical or typographical errors. IBM shall have no
responsibility to update this information. THIS DOCUMENT IS DISTRIBUTED "AS IS"
WITHOUT ANY WARRANTY, EITHER EXPRESS OR IMPLIED. IN NO EVENT SHALL IBM BE LIABLE
FOR ANY DAMAGE ARISING FROM THE USE OF THIS INFORMATION, INCLUDING BUT NOT
LIMITED TO, LOSS OF DATA, BUSINESS INTERRUPTION, LOSS OF PROFIT OR LOSS OF
OPPORTUNITY.

IBM products and services are warranted according to the terms and conditions of
the agreements under which they are provided.

References in this document to IBM products, programs, or services does not
imply that IBM intends to make such products, programs, or services available in
all countries in which IBM operates or does business.

Information concerning non-IBM products was obtained from the suppliers of those
products, their published announcements, or other publicly available sources.
IBM has not tested those products in connection with this publication and cannot
confirm the accuracy of performance, compatibility or any other claims related
to non-IBM products. Questions on the capabilities of non-IBM products should be
addressed to the suppliers of those products. IBM does not warrant the quality
of any third-party products, or the ability of any such third-party products to
interoperate with IBM's products. IBM EXPRESSLY DISCLAIMS ALL WARRANTIES,
EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

The provision of the information contained herein is not intended to, and does
not, grant any right or license under any IBM patents, copyrights, trademarks,
or other intellectual property right.

IBM, the IBM logo, ibm.com, Aspera®, Bluemix, Blueworks Live, CICS, Clearcase,
Cognos®, DOORS®, Emptoris®, Enterprise Document Management System™, FASP®,
FileNet®, Global Business Services ®, Global Technology Services ®, IBM
ExperienceOne™, IBM SmartCloud®, IBM Social Business®, Information on Demand,
ILOG, Maximo®, MQIntegrator®, MQSeries®, Netcool®, OMEGAMON, OpenPower,
PureAnalytics™, PureApplication®, pureCluster™, PureCoverage®, PureData®,
PureExperience®, PureFlex®, pureQuery®, pureScale®, PureSystems®, QRadar®,
Rational®, Rhapsody®, Smarter Commerce®, SoDA, SPSS, Sterling Commerce®,
StoredIQ, Tealeaf®, Tivoli®, Trusteer®, Unica®, urban{code}®, Watson,
WebSphere®, Worklight®, X-Force® and System z® Z/OS, are trademarks of
International Business Machines Corporation, registered in many jurisdictions
worldwide.

Other product and service names might be trademarks of IBM or other companies. A
current list of IBM trademarks is available on the Web at "Copyright and
trademark information" at: www.ibm.com/legal/copytrade.shtml.

All trademarks or copyrights mentioned herein are the possession of their
respective owners and IBM makes no claim of ownership by the mention of products
that contain these marks.

