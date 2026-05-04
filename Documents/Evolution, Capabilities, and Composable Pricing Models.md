# MDR and AI impact on pricing

*Converted from NotebookLM export: Evolution, Capabilities, and Composable Pricing Models.html*

## Notebook Summary

These sources examine the shifting landscape of **Managed Detection and Response (MDR)** as providers integrate **artificial intelligence** and **preemptive security** to combat sophisticated threats like deepfakes and disinformation. To remain competitive in a maturing market, vendors are moving beyond reactive monitoring toward **autonomous deception** and **predictive threat intelligence**. While AI-driven automation improves service speed and breadth, it is not expected to reduce costs due to the significant capital investments required and the continued necessity of **human expertise**. Consequently, the reports advocate for a **composable pricing model** that blends subscriptions with usage-based fees, as pure outcome-based pricing often fails due to measurement complexities. Ultimately, security leaders are encouraged to prioritize **transparency** and **measurable risk reduction** when evaluating advanced service offerings.


---

## Exchange 1

### Prompt

> consider these attached sources, with the consideration for the construct and definition of what MDR services are. think about major capabilities that are consistent in both the market guide but that are considered standard across many providers. we want to also start to think about the preemptive threat intelligence, that would have traditionally been a capability unique to threat research companies such as recorded future that can realistically be achieved largely through AI agents now. now provide a detailed note on applicable pricing models for each of the capabilities and a detailed set of definitions for the capabilities

### Response

**Construct and Definition of MDR Services** Managed Detection and Response (MDR) services provide organizations with comprehensive detection coverage, the ability to investigate detections at scale, and a primary focus on actionable response. At its core, the value proposition of an MDR provider is to deliver **context, understanding, insight, and validation** of the alerts surfaced by security tools.

While AI and automation are rapidly transforming these services, MDR fundamentally relies on a blend of human analysis and technology. AI is best utilized as a data enrichment assistant, whereas the human-led guidance, business context, and remediation advice remain crucial differentiators that organizations expect. The primary operational objectives of MDR are to reduce Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR).

**Detailed Definitions of Standard and Emerging Capabilities** The capabilities of MDR providers span from standard threat detection to highly advanced, AI-enabled preemptive defense:

  * **Standard Threat Detection, Investigation, and Response (TDIR):** These are the baseline capabilities expected from providers, including real-time correlation of signals from endpoints, networks, identities, and cloud environments to identify threats. It also involves alert triage, false positive identification, and guided investigation capabilities.
  * **Preemptive Threat Intelligence (AI-Driven):** Traditionally a reactive capability or the domain of specialized threat re companies, preemptive threat intelligence is now largely achieved through domain-specific AI and Large Language Models (LLMs). This capability involves predictive analytics that use historical data and machine learning to predict future threats and vulnerabilities. AI facilitates behavior-based prioritization, anomaly detection across user activities, and the rapid processing of massive threat intelligence data feeds to predict and preempt attacks.
  * **Autonomous Deception and Automated Moving Target Defense (AMTD):** This capability shifts MDR to a preventative stance by using AI-powered analytics to create decoy environments, fake data, and misleading network traffic. It is designed to trick attackers into revealing their tactics, techniques, and procedures (TTPs) while dynamically altering the attack surface to complicate exploitation efforts.
  * **Disinformation Security:** An emerging capability to detect and respond to disinformation campaigns, which include impersonation attacks (voice, image, identity), deepfakes, and narrative attacks designed to evade traditional detection and mislead organizations.

**Applicable Pricing Models for MDR Capabilities** While "outcome-based pricing" is a trending concept, it often fails in practice due to the complexity and cost of measuring success, obtaining agreement on attributions, and the unpredictable nature of revenue and budgeting. Instead, providers are encouraged to use a **"composable" pricing approach** —a transparent hybrid model utilizing familiar billing components tailored to specific capabilities:

  * **Subscriptions (Base Revenue Floor):** This model charges for the ongoing delivery of predictable elements, such as core human analyst time, managed services bundles, non-AI software, and specific AI tool fees.
    * _Applicable Capabilities:_ **Standard TDIR** , **Disinformation Security monitoring** , and **Deception-as-a-Service**. Since these require continuous human-in-the-loop oversight and baseline platform access, a recurring subscription provides predictable budgeting for the client and stable revenue for the provider.
  * **Usage-Based / Consumption-Based Fees:** This involves variable costs driven by the actual consumption of resources, such as API calls, data volume ingested, compute hours, and AI inference charges.
    * _Applicable Capabilities:_ **Preemptive Threat Intelligence**. Because predictive threat intelligence relies heavily on ingesting vast amounts of telemetry, external threat feeds, and running intensive domain-specific AI algorithms to predict attacks, charging based on data volume or AI compute usage aligns the cost directly with the computational effort provided.
  * **Fixed Delivery Fees:** One-time costs for design, setup, and implementation.
    * _Applicable Capabilities:_ The initial deployment of **Autonomous Deception and AMTD** environments, integration of complex telemetry pipelines, and customized AI playbook creation.
  * **Success Fees / Output-Based Pricing (Fees at Risk):** This involves bonuses, penalties, or per-unit pricing based on achieving major engagement objectives or completed units of work.
    * _Applicable Capabilities:_ **Standard TDIR** and **AI Automations**. If an AI agent automatically resolves a specific class of security incident without human intervention, the provider might charge an output-based fee _per resolution_. Providers can also tie success bonuses to verified reductions in MTTD and MTTR, directly linking the pricing to the efficiency gains created by AI.

**A Crucial Note on AI and MDR Pricing Realities** Although organizations might assume that the integration of AI agents will drive down the cost of MDR services, **leadership hopes for cost savings will likely go unrealized**. Implementing AI requires massive capital investments and high margins from providers. Rather than lowering prices, providers will use AI to handle larger alert volumes, expand service coverage to more complex use cases, and increase response speed without increasing their human headcount. Buyers should evaluate the pricing models based on the expanded scope and visibility the service provides, rather than expecting a budget reduction.


---

## Exchange 2

### Prompt

> Why won't AI integration lead to lower MDR pricing?

### Response

The integration of AI into Managed Detection and Response (MDR) services is unlikely to lead to lower pricing for several key reasons:

  * **High Capital Investments:** Developing and implementing AI requires massive funding and capital investments. Because of the high costs of experimentation and the need to support these new technologies, MDR providers require high margins to sustain their AI initiatives, preventing them from lowering subscription costs.
  * **The Continued Need for Human Expertise:** While AI acts as a powerful data enrichment assistant, the core value of MDR relies on human-driven advisory, business context, and remediation guidance. Because the nature of human analysis expected from MDR providers remains essential, their overhead costs for staffing will not be reduced.
  * **Expanding Scope Rather Than Cutting Costs:** Instead of translating AI efficiency into budget reductions, providers are using AI to increase their throughput. AI allows providers to handle much larger alert volumes, increase response speeds, and expand their service coverage to include more complex use cases without needing to increase their human headcount.
  * **Historical Precedent of Automation:** Much like previous waves of heavy automation did not result in bringing prices down for MDR services, AI is expected to follow the exact same trend.
  * **Risk of Increased Costs from Poor Implementation:** If an MDR provider struggles to effectively integrate AI automations, it will inevitably lead to an increased volume of false positives and a degradation in the quality of alert reports. Dealing with these inefficiencies can actually trigger increased costs rather than reducing them.

Buyers are advised to evaluate AI-enabled MDR services based on the **expanded visibility and enhanced maturity** the service provides, rather than expecting a budget reduction.


---

## Exchange 3

### Prompt

> How can I measure the ROI of AI-augmented MDR services?

### Response

Because AI integration in Managed Detection and Response (MDR) services is unlikely to reduce your overall budget, **measuring ROI requires shifting your focus from cost savings to evaluating enhancements in speed, service quality, and expanded operational scope**.

To effectively measure the ROI of AI-augmented MDR services, you should evaluate the following metrics and operational improvements:

  * **Reductions in Detection and Response Times:** Measure the service's impact on core speed metrics. A primary indicator of ROI is a demonstrable reduction in Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR), as well as adherence to improved SLA times for these phases.
  * **Resolution Autonomy and Efficiency:** Refactor your KPIs to measure how much work the MDR provider handles independently. Track the ability of the service to resolve discovered issues without needing to involve your internal security teams, and monitor the volume of required clarifications you have to seek regarding their service deliverables.
  * **Expanded Visibility and Threat Coverage:** Evaluate ROI based on the service's ability to investigate a larger pool of alerts and provide extended visibility across your environment, allowing the provider to cover more complex use cases without increasing your internal overhead.
  * **Quality of Alerts and AI Outputs:** Organizations previously measuring ROI based on the raw volume of alerts processed must adapt, as AI will increasingly automate simple triage. Instead, monitor the _quality_ of the outputs. Track metrics around service degradation, such as increases in false positives, AI hallucinations, or degraded alert descriptions, to ensure the AI isn't simply generating noise.
  * **Pre- and Post-Deployment Resource Shifts:** Measure your internal resource requirements and quality metrics from before and after the AI-augmented service was deployed. An effective service should allow your internal analysts to upskill and handle more complex tasks, rather than simply transferring the burden of reviewing poor AI outputs back to your staff.
  * **Impact-Based KPIs for Emerging Threats:** For advanced capabilities like disinformation security, measure ROI using impact-based KPIs that quantify the prevention of consequential damages to your organization's finances, reputation, and overall brand perception.

Ultimately, it is highly recommended to negotiate and update your KPIs with your provider so that they **adequately represent the true value of the service contribution—such as human-led context, understanding, and remediation guidance—rather than just reflecting the performance of their AI technology**. To build trust in the investment, the AI must demonstrate measurable improvements in speed and accuracy, ideally proven through business impact analysis or performance benchmarking.


---

## Exchange 4

### Prompt

> why will the adoption and development of ai capabilities not be an increased revenue source for MDR providers. consider the outcomes of addition AI to replace capabilities that were largely automated through a SOAR platform traditionally. and as a result there is no real additional value that could justify an increase in pricing. Also factor in that the capability is often adding additional cost because of the development and platform costs but has not been implemented in a manner that allows for the reduction in resources necessary to deliver the core services.

### Response

The adoption and development of AI capabilities are unlikely to generate increased revenue for Managed Detection and Response (MDR) providers because these technologies largely replace existing automated functions, introduce massive overhead costs, and fail to reduce the human headcount required to deliver the core service.

**Replacement of Traditional Automation Offers No New Value** AI tools in the security operations center (SOC) are increasingly used for automated triage of well-known security issues, guided investigations, and false positive identification. Because these functions were traditionally handled by heavy automation (such as SOAR platforms), integrating AI is often viewed as a back-end operational upgrade rather than a net-new capability. Buyers expect MDR providers to efficiently handle basic triage, so substituting a legacy automation platform with an AI agent does not change the baseline deliverable. As a result, **buyers do not perceive enough itional value to justify an increase in pricing** , and much like previous waves of heavy automation did not bring prices down or allow for higher premiums, neither will AI.

**High Development and Platform Costs** Implementing AI requires **massive capital investments and high margins** from MDR providers. Providers must bear the high costs of ongoing experimentation, developing custom-built automations, and supporting expensive domain-specific platforms. While the provider absorbs the financial risk and platform costs of developing these tools, C-level executives on the buying side actually expect AI to yield cost savings. This misalignment means providers cannot easily pass their R&D and platform costs onto the customer through increased revenue.

**No Reduction in Core Human Resources** The fundamental value proposition of an MDR provider is to deliver **context, understanding, insight, and validation** —tasks that are still best suited for human analysis. While AI acts as a powerful data enrichment assistant, buyers explicitly demand human-driven advisory, business-centric context, and remediation guidance. Because buyers will not tolerate purely machine-driven deliverables, **the nature of the human analysis expected from providers remains essential, meaning their overhead costs for staffing cannot be reduced**.

In fact, AI integration often expands the service scope by allowing providers to process much larger alert volumes and investigate more complex use cases. Rather than reducing headcount, the expanded visibility and complexity of alerts passed by AI often require the provider (and the customer) to upskill analysts and maintain or even increase staffing levels to properly handle the increased throughput.

**The Risk of Inflated Costs from Poor Implementation** Finally, if AI capabilities are not implemented flawlessly, they actively drain resources. Providers that struggle to effectively integrate AI inevitably suffer from service degradation, leading to an increased volume of false positives, AI hallucinations, and poor-quality alert descriptions. Because the MDR provider is ultimately responsible for validating the work carried out by the AI, **dealing with these machine-generated inefficiencies requires more human intervention, which triggers increased operating costs** rather than reducing the resources necessary to deliver the service.
