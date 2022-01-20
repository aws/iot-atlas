---
title: "IoT Atlas Bot"
hidden: true
type: page
---

## IoT Atlas Bot

The _IotAtlasBot_ is the name of the IoT Atlas web crawler. This bot is used periodically to check the validity all links on the IoT Atlas site.

Your site was accessed for specific links present within the IoT Atlas to verify they are still valid and accessible. Access can occur in three different ways. First, content creators can run a verification set of steps on all IoT Atlas content from their local development environment. This can originate from any IP address on the Internet. You can verify this by checking the `User-Agent` field in your web server log files.

Second, when content is ready for inclusion, a GitHub pull request will initiate a [GitHub Action](https://github.com/features/actions) to pre-check the content prior to publishing. The IP addresses seen will originate from GitHub allocated public IP addresses.

And finally, once a content pull request has completed, the publishing pipeline will complete a final link check just prior to a new version of content being made publicly available. This is done via [AWS CodePipe](https://aws.amazon.com/codepipeline/) in the Northern Virginia region. The IP addresses will be those associated with the `us-east-1` region from the [AWS IP address ranges JSON file](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html#aws-ip-download).

If you are seeing excessive requests from the bot, please open an [issue](https://github.com/aws/iot-atlas/issues/new) with details on how we can contact you to remediate.
