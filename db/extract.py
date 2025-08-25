import numpy as np
import cv2 as cv
import fitz  # PyMuPDF

########################## pdf extract calculate func ##########################

#Recursively finds the boundaries of each section in a binarized image
#Mainly used to identify blocks containing text or graphics
def find_section_borders(img_binary:np.array, 
                    min_w:float=0.0, min_h:float=0.0, 
                    min_dx:float=15.0, min_dy:float=15.0): 

    def cut_sections(arr:np.array, top_left:tuple, res:list, 
                    min_w:float, min_h:float, min_dx:float, min_dy:float):
        x0, y0 = top_left
        h, w = arr.shape

        #Vertical projection to find horizontal gaps
        projection = np.count_nonzero(arr==255, axis=1)
        pos_y = identify_gaps(projection, min_w, min_dy)
        if not pos_y: return        

        arr_y0, arr_y1 = pos_y
        for r0, r1 in zip(arr_y0, arr_y1):
            x_arr = arr[r0:r1, 0:w]
            projection = np.count_nonzero(x_arr==255, axis=0)
            pos_x = identify_gaps(projection, min_h, min_dx)
            if not pos_x: continue

            arr_x0, arr_x1 = pos_x
            if len(arr_x0)==1:
                #Append section coordinates to results
                res.append((x0+arr_x0[0], y0+r0, x0+arr_x1[0], y0+r1))
                continue
            
            for c0, c1 in zip(arr_x0, arr_x1):
                y_arr = arr[r0:r1, c0:c1]
                top_left = (x0+c0, y0+r0)
                cut_sections(y_arr, top_left, res, min_w, min_h, min_dx, min_dy)

    res = []
    cut_sections(arr=img_binary, top_left=(0, 0), res=res, 
            min_w=min_w, min_h=min_h, min_dx=min_dx, min_dy=min_dy)
    return res

#Finds start and end indices of objects based on minimum value and gap thresholds
#Used to detect the positions of objects within the projection array
def identify_gaps(arr_values:np.array, min_value:float, min_gap:float):

    idx = np.where(arr_values>min_value)[0]
    if not len(idx): return

    gaps = idx[1:] - idx[0:-1]
    gap_idx = np.where(gaps>min_gap)[0]
    segment_start = idx[gap_idx]
    segment_end = idx[gap_idx+1]

    starts = np.insert(segment_end, 0, idx[0])
    ends = np.append(segment_start, idx[-1])
    ends += 1 

    return starts, ends

class daconCustomExtractor:
    def __init__(self, page: fitz.Page) -> None:
        self._page = page

    #Convert a specific region of the page into a pixmap based on bounding box
    #Pixmap = rasterized image representation of the document section
    def clip_page_to_pixmap(self, bbox: fitz.Rect = None, zoom: float = 3.0):
        if bbox is None:
            clip_bbox = self._page.rect
        elif self._page.rotation:
            clip_bbox = bbox * self._page.rotation_matrix
        else:
            clip_bbox = bbox
        clip_bbox = self._page.rect & clip_bbox
        matrix = fitz.Matrix(zoom, zoom)
        pix = self._page.get_pixmap(clip=clip_bbox, matrix=matrix)
        return pix

    #Detect SVG-like contours by analyzing external/internal boundaries of each image
    #Each page → converted to grayscale → binarized → boundary detection
    #Then clipped regions are returned
    def detect_svg_contours(self, page_num, min_svg_gap_dx: float, min_svg_gap_dy: float, min_w: float, min_h: float):
        
        pixmap = self.clip_page_to_pixmap(zoom=1.0)
        src = self._pixmap_to_cv_image(pixmap)
        gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(gray, 253, 255, cv.THRESH_BINARY_INV)
        external_bboxes = find_section_borders(binary, min_dx=min_svg_gap_dx, min_dy=min_svg_gap_dy)

        return external_bboxes
    
    @staticmethod
    def _pixmap_to_cv_image(pixmap: fitz.Pixmap):
        #Convert PyMuPDF Pixmap to an OpenCV image (numpy array)
        img_byte = pixmap.tobytes()
        return cv.imdecode(np.frombuffer(img_byte, np.uint8), cv.IMREAD_COLOR)